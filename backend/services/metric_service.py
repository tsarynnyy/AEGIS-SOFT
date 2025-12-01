from typing import List, Optional
from repositories import MetricRepository
from models import MetricSample, MetricSampleCreate
from datetime import datetime, timedelta


class MetricService:
    def __init__(self, metric_repo: MetricRepository):
        self.metric_repo = metric_repo
    
    async def ingest_sample(self, sample_create: MetricSampleCreate) -> MetricSample:
        """
        Ingest a single metric sample.
        """
        sample_data = sample_create.dict()
        sample_data['ingested_at'] = datetime.utcnow()
        
        created = await self.metric_repo.create(sample_data)
        return MetricSample(**created)
    
    async def ingest_samples_bulk(self, samples: List[MetricSampleCreate]) -> int:
        """
        Bulk ingest metric samples.
        Returns count of ingested samples.
        """
        if not samples:
            return 0
        
        samples_data = [
            {**s.dict(), 'ingested_at': datetime.utcnow()}
            for s in samples
        ]
        
        count = await self.metric_repo.bulk_create(samples_data)
        return count
    
    async def get_member_metrics(
        self,
        member_id: str,
        metric_type: Optional[str] = None,
        days: int = 7
    ) -> List[MetricSample]:
        """
        Get metrics for a member.
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if metric_type:
            metrics_data = await self.metric_repo.find_by_member_and_type(
                member_id, metric_type, start_date, end_date
            )
        else:
            metrics_data = await self.metric_repo.find_by_member(
                member_id, start_date, end_date
            )
        
        return [MetricSample(**m) for m in metrics_data]
    
    async def get_latest_metric(
        self,
        member_id: str,
        metric_type: str
    ) -> Optional[MetricSample]:
        """
        Get latest metric of specific type for member.
        """
        metrics_data = await self.metric_repo.get_latest_by_type(member_id, metric_type, limit=1)
        if not metrics_data:
            return None
        return MetricSample(**metrics_data[0])
