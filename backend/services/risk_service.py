from typing import List, Dict, Any, Optional
from repositories import RiskRepository, MetricRepository
from models import RiskEvent, RiskEventCreate, RiskTier, RiskFactor, MetricType
from datetime import datetime, timedelta
import statistics


class RiskService:
    """
    Risk detection service with statistical baseline analysis.
    Mode: 'template' for MVP (deterministic, template-based explanations).
    Future: Add 'llm' mode for AI-powered explanations.
    """
    
    def __init__(self, risk_repo: RiskRepository, metric_repo: MetricRepository):
        self.risk_repo = risk_repo
        self.metric_repo = metric_repo
        self.explanation_mode = "template"  # "template" | "llm"
    
    async def analyze_member_risk(self, member_id: str, org_id: str) -> Optional[RiskEvent]:
        """
        Analyze member's recent metrics and detect risk.
        Returns RiskEvent if anomalies detected, None if all normal.
        """
        # Get recent metrics (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        factors: List[RiskFactor] = []
        
        # Analyze HRV (Heart Rate Variability)
        hrv_factor = await self._analyze_hrv(member_id, start_date, end_date)
        if hrv_factor:
            factors.append(hrv_factor)
        
        # Analyze Sleep Efficiency
        sleep_factor = await self._analyze_sleep(member_id, start_date, end_date)
        if sleep_factor:
            factors.append(sleep_factor)
        
        # Analyze Steps/Activity
        steps_factor = await self._analyze_steps(member_id, start_date, end_date)
        if steps_factor:
            factors.append(steps_factor)
        
        # If no factors, member is in good status
        if not factors:
            return None
        
        # Calculate composite risk score
        score = self._calculate_risk_score(factors)
        tier = self._determine_tier(score, factors)
        
        # Generate explanation
        explanation = self._generate_explanation(factors, tier)
        
        # Suggest actions
        actions = self._suggest_actions(tier, factors)
        
        # Create risk event
        risk_data = {
            'member_id': member_id,
            'org_id': org_id,
            'tier': tier,
            'score': score,
            'factors': [f.dict() for f in factors],
            'explanation_text': explanation,
            'suggested_actions': actions,
            'detected_at': datetime.utcnow()
        }
        
        created = await self.risk_repo.create(risk_data)
        return RiskEvent(**created)
    
    async def _analyze_hrv(self, member_id: str, start_date: datetime, end_date: datetime) -> Optional[RiskFactor]:
        """
        Analyze HRV trends. Lower HRV can indicate stress or declining health.
        """
        metrics = await self.metric_repo.find_by_member_and_type(
            member_id, MetricType.HRV, start_date, end_date
        )
        
        if len(metrics) < 7:
            return None  # Not enough data
        
        # Sort by timestamp
        metrics = sorted(metrics, key=lambda m: m['timestamp'])
        
        # Get recent 7 days and baseline (previous 14-30 days)
        recent = [m['value_num'] for m in metrics[-7:] if m['value_num']]
        baseline = [m['value_num'] for m in metrics[:-7] if m['value_num']]
        
        if not recent or not baseline:
            return None
        
        recent_avg = statistics.mean(recent)
        baseline_avg = statistics.mean(baseline)
        
        # Calculate percentage change
        delta = (recent_avg - baseline_avg) / baseline_avg if baseline_avg > 0 else 0
        
        # Significant drop (>15%) is concerning
        if delta < -0.15:
            return RiskFactor(
                type="hrv_drop",
                window_days=7,
                delta=delta,
                actual_value=recent_avg,
                baseline_value=baseline_avg,
                severity=min(abs(delta) / 0.3, 1.0)  # Normalize to 0-1
            )
        
        return None
    
    async def _analyze_sleep(self, member_id: str, start_date: datetime, end_date: datetime) -> Optional[RiskFactor]:
        """
        Analyze sleep efficiency. Low efficiency indicates poor sleep quality.
        """
        metrics = await self.metric_repo.find_by_member_and_type(
            member_id, MetricType.SLEEP_EFFICIENCY, start_date, end_date
        )
        
        if len(metrics) < 4:
            return None
        
        # Get last 7 nights
        recent = [m['value_num'] for m in metrics[-7:] if m['value_num']]
        if not recent:
            return None
        
        # Count nights with poor efficiency (<0.78)
        poor_nights = sum(1 for eff in recent if eff < 0.78)
        avg_efficiency = statistics.mean(recent)
        
        # 4+ poor nights out of 7 is concerning
        if poor_nights >= 4:
            return RiskFactor(
                type="sleep_efficiency_low",
                window_days=7,
                threshold=0.78,
                actual_value=avg_efficiency,
                severity=poor_nights / 7.0
            )
        
        return None
    
    async def _analyze_steps(self, member_id: str, start_date: datetime, end_date: datetime) -> Optional[RiskFactor]:
        """
        Analyze step count trends. Declining activity is a wellness concern.
        """
        metrics = await self.metric_repo.find_by_member_and_type(
            member_id, MetricType.STEPS, start_date, end_date
        )
        
        if len(metrics) < 14:
            return None
        
        metrics = sorted(metrics, key=lambda m: m['timestamp'])
        recent = [m['value_num'] for m in metrics[-7:] if m['value_num']]
        baseline = [m['value_num'] for m in metrics[:-7] if m['value_num']]
        
        if not recent or not baseline:
            return None
        
        recent_avg = statistics.mean(recent)
        baseline_avg = statistics.mean(baseline)
        delta = (recent_avg - baseline_avg) / baseline_avg if baseline_avg > 0 else 0
        
        # Significant drop (>25%) is concerning
        if delta < -0.25:
            return RiskFactor(
                type="steps_decline",
                window_days=7,
                delta=delta,
                actual_value=recent_avg,
                baseline_value=baseline_avg,
                severity=min(abs(delta) / 0.4, 1.0)
            )
        
        return None
    
    def _calculate_risk_score(self, factors: List[RiskFactor]) -> float:
        """
        Calculate composite risk score (0-100) from factors.
        """
        if not factors:
            return 0.0
        
        # Weight factors by severity and count
        total_severity = sum(f.severity or 0.5 for f in factors)
        factor_count_weight = min(len(factors) / 3.0, 1.0)  # More factors = higher risk
        
        # Composite score
        score = (total_severity / len(factors)) * 100 * (0.7 + 0.3 * factor_count_weight)
        return min(score, 100.0)
    
    def _determine_tier(self, score: float, factors: List[RiskFactor]) -> RiskTier:
        """
        Determine risk tier based on score and factors.
        """
        if score >= 70 or len(factors) >= 3:
            return RiskTier.RED
        elif score >= 40 or len(factors) >= 2:
            return RiskTier.YELLOW
        else:
            return RiskTier.GREEN
    
    def _generate_explanation(self, factors: List[RiskFactor], tier: RiskTier) -> str:
        """
        Generate human-readable explanation (template mode).
        """
        if not factors:
            return "All wellness indicators are within normal range."
        
        parts = []
        for factor in factors:
            if factor.type == "hrv_drop":
                delta_pct = abs(factor.delta * 100)
                parts.append(f"{factor.window_days}-day HRV down {delta_pct:.0f}% vs baseline")
            elif factor.type == "sleep_efficiency_low":
                parts.append(f"Poor sleep efficiency in recent nights (avg {factor.actual_value:.2f})")
            elif factor.type == "steps_decline":
                delta_pct = abs(factor.delta * 100)
                parts.append(f"Activity level down {delta_pct:.0f}% (recent avg: {factor.actual_value:.0f} steps)")
        
        explanation = "; ".join(parts) + "."
        
        if tier == RiskTier.RED:
            prefix = "⚠️ Multiple wellness concerns detected: "
        elif tier == RiskTier.YELLOW:
            prefix = "⚡ Wellness alert: "
        else:
            prefix = "✓ Wellness check: "
        
        return prefix + explanation
    
    def _suggest_actions(self, tier: RiskTier, factors: List[RiskFactor]) -> List[str]:
        """
        Suggest human actions based on risk tier.
        """
        actions = []
        
        if tier == RiskTier.RED:
            actions.append("Contact member immediately")
            actions.append("Schedule care team review")
            actions.append("Check for recent health changes")
        elif tier == RiskTier.YELLOW:
            actions.append("Check in with member within 24 hours")
            actions.append("Review recent activities and sleep patterns")
        else:
            actions.append("Continue monitoring")
        
        # Add specific actions based on factors
        factor_types = [f.type for f in factors]
        if "sleep_efficiency_low" in factor_types:
            actions.append("Discuss sleep quality and environment")
        if "steps_decline" in factor_types:
            actions.append("Encourage light physical activity")
        if "hrv_drop" in factor_types:
            actions.append("Check for stress or illness symptoms")
        
        return actions
    
    async def get_member_alerts(
        self,
        member_id: str,
        limit: int = 50
    ) -> List[RiskEvent]:
        """
        Get risk events/alerts for a member.
        """
        alerts_data = await self.risk_repo.find_by_member(member_id, limit=limit)
        return [RiskEvent(**a) for a in alerts_data]
    
    async def get_latest_member_risk(self, member_id: str) -> Optional[RiskEvent]:
        """
        Get latest risk event for a member.
        """
        alert_data = await self.risk_repo.get_latest_by_member(member_id)
        if not alert_data:
            return None
        return RiskEvent(**alert_data)
