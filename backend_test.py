#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Aegis AI Wellness Platform
Tests all major endpoints with demo data
"""

import requests
import json
import sys
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://aegis-monitor.preview.emergentagent.com/api"
TEST_EMAIL = "demo.member0@aegis-demo.com"
TEST_PASSWORD = "demo123"

# Test members with different risk patterns
TEST_MEMBERS = {
    "healthy": "demo.member0@aegis-demo.com",
    "declining_hrv": "demo.member3@aegis-demo.com",  # Patricia Brown
    "poor_sleep": "demo.member5@aegis-demo.com",     # Jennifer Garcia  
    "low_activity": "demo.member7@aegis-demo.com",   # Linda Davis
    "mixed_concerns": "demo.member8@aegis-demo.com"  # David Rodriguez
}

class AegisAPITester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.current_user = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", error=""):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    Details: {details}")
        if error:
            print(f"    Error: {error}")
        print()
    
    def make_request(self, method, endpoint, **kwargs):
        """Make authenticated request"""
        url = f"{BASE_URL}{endpoint}"
        
        # Add auth header if we have a token
        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f"Bearer {self.access_token}"
            kwargs['headers'] = headers
            
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except Exception as e:
            return None
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response = self.make_request('GET', '/health')
            if response and response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    self.log_test("Health Check", True, f"Service: {data.get('service')}")
                    return True
                else:
                    self.log_test("Health Check", False, error="Status not healthy")
                    return False
            else:
                self.log_test("Health Check", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return False
        except Exception as e:
            self.log_test("Health Check", False, error=str(e))
            return False
    
    def test_login(self, email=TEST_EMAIL, password=TEST_PASSWORD):
        """Test user login"""
        try:
            payload = {
                "email": email,
                "password": password
            }
            
            response = self.make_request('POST', '/auth/login', json=payload)
            
            if response and response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                self.refresh_token = data.get('refresh_token')
                self.current_user = data.get('user')
                
                if self.access_token and self.current_user:
                    self.log_test("User Login", True, f"User: {self.current_user.get('email')}")
                    return True
                else:
                    self.log_test("User Login", False, error="Missing token or user data")
                    return False
            else:
                error_msg = response.json().get('detail', 'Unknown error') if response else 'No response'
                self.log_test("User Login", False, error=f"HTTP {response.status_code if response else 'No response'}: {error_msg}")
                return False
                
        except Exception as e:
            self.log_test("User Login", False, error=str(e))
            return False
    
    def test_get_current_user(self):
        """Test get current user profile"""
        try:
            response = self.make_request('GET', '/auth/me')
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('email') == self.current_user.get('email'):
                    self.log_test("Get Current User", True, f"Email: {data.get('email')}")
                    return True
                else:
                    self.log_test("Get Current User", False, error="User data mismatch")
                    return False
            else:
                self.log_test("Get Current User", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return False
                
        except Exception as e:
            self.log_test("Get Current User", False, error=str(e))
            return False
    
    def test_refresh_token(self):
        """Test token refresh"""
        try:
            payload = {
                "refresh_token": self.refresh_token
            }
            
            response = self.make_request('POST', '/auth/refresh', json=payload)
            
            if response and response.status_code == 200:
                data = response.json()
                new_token = data.get('access_token')
                if new_token:
                    old_token = self.access_token
                    self.access_token = new_token
                    self.log_test("Token Refresh", True, "New access token received")
                    return True
                else:
                    self.log_test("Token Refresh", False, error="No access token in response")
                    return False
            else:
                self.log_test("Token Refresh", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return False
                
        except Exception as e:
            self.log_test("Token Refresh", False, error=str(e))
            return False
    
    def test_get_member_profile(self):
        """Test get member profile"""
        try:
            response = self.make_request('GET', '/members/me')
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('first_name') and data.get('last_name'):
                    member_id = data.get('id')
                    self.current_member_id = member_id
                    self.log_test("Get Member Profile", True, f"Member: {data.get('first_name')} {data.get('last_name')} (ID: {member_id})")
                    return data
                else:
                    self.log_test("Get Member Profile", False, error="Missing member data")
                    return None
            else:
                self.log_test("Get Member Profile", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Member Profile", False, error=str(e))
            return None
    
    def test_get_member_by_id(self, member_id):
        """Test get member by ID"""
        try:
            response = self.make_request('GET', f'/members/{member_id}')
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('id') == member_id:
                    self.log_test("Get Member by ID", True, f"Member: {data.get('first_name')} {data.get('last_name')}")
                    return data
                else:
                    self.log_test("Get Member by ID", False, error="Member ID mismatch")
                    return None
            else:
                self.log_test("Get Member by ID", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Member by ID", False, error=str(e))
            return None
    
    def test_get_member_metrics(self, member_id, metric_type=None, days=7):
        """Test get member health metrics"""
        try:
            params = {'days': days}
            if metric_type:
                params['metric_type'] = metric_type
                
            response = self.make_request('GET', f'/members/{member_id}/metrics', params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    filter_desc = f" (filtered by {metric_type})" if metric_type else ""
                    self.log_test(f"Get Member Metrics ({days} days){filter_desc}", True, f"Retrieved {len(data)} metrics")
                    return data
                else:
                    self.log_test(f"Get Member Metrics ({days} days)", False, error="Response not a list")
                    return None
            else:
                self.log_test(f"Get Member Metrics ({days} days)", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test(f"Get Member Metrics ({days} days)", False, error=str(e))
            return None
    
    def test_analyze_risk(self, member_id):
        """Test risk analysis"""
        try:
            response = self.make_request('POST', f'/members/{member_id}/analyze-risk')
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('tier') or data.get('risk_tier'):
                        risk_tier = data.get('tier') or data.get('risk_tier')
                        explanation = data.get('explanation_text') or data.get('explanation', 'No explanation')
                        self.log_test("Risk Analysis", True, f"Risk Tier: {risk_tier}, Explanation: {explanation[:100]}...")
                        return data
                    else:
                        # Check if it's a "no risk" response with detail message
                        if data.get('detail') and "No risk detected" in data.get('detail'):
                            self.log_test("Risk Analysis", True, "No risk detected - member is healthy")
                            return {"risk_tier": "green", "explanation": "No risk detected"}
                        else:
                            self.log_test("Risk Analysis", False, error="Missing risk data")
                            return None
                except:
                    # Handle non-JSON response
                    if response.text and "No risk detected" in response.text:
                        self.log_test("Risk Analysis", True, "No risk detected - member is healthy")
                        return {"risk_tier": "green", "explanation": "No risk detected"}
                    else:
                        self.log_test("Risk Analysis", False, error="Invalid response format")
                        return None
            else:
                self.log_test("Risk Analysis", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Risk Analysis", False, error=str(e))
            return None
    
    def test_get_current_risk(self, member_id):
        """Test get current risk status"""
        try:
            response = self.make_request('GET', f'/members/{member_id}/current-risk')
            
            if response and response.status_code == 200:
                data = response.json()
                if data and data.get('risk_tier'):
                    risk_tier = data.get('risk_tier')
                    self.log_test("Get Current Risk", True, f"Current Risk Tier: {risk_tier}")
                    return data
                elif data is None:
                    self.log_test("Get Current Risk", True, "No current risk events")
                    return None
                else:
                    self.log_test("Get Current Risk", False, error="Invalid risk data")
                    return None
            else:
                self.log_test("Get Current Risk", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Current Risk", False, error=str(e))
            return None
    
    def test_get_member_alerts(self, member_id):
        """Test get member alerts"""
        try:
            response = self.make_request('GET', f'/members/{member_id}/alerts')
            
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Member Alerts", True, f"Retrieved {len(data)} alerts")
                    return data
                else:
                    self.log_test("Get Member Alerts", False, error="Response not a list")
                    return None
            else:
                self.log_test("Get Member Alerts", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Member Alerts", False, error=str(e))
            return None
    
    def test_get_member_devices(self, member_id):
        """Test get member devices"""
        try:
            response = self.make_request('GET', f'/members/{member_id}/devices')
            
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Member Devices", True, f"Retrieved {len(data)} devices")
                    return data
                else:
                    self.log_test("Get Member Devices", False, error="Response not a list")
                    return None
            else:
                self.log_test("Get Member Devices", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Member Devices", False, error=str(e))
            return None
    
    def test_get_member_consents(self, member_id):
        """Test get member consents"""
        try:
            response = self.make_request('GET', f'/members/{member_id}/consents')
            
            if response and response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Member Consents", True, f"Retrieved {len(data)} consents")
                    return data
                else:
                    self.log_test("Get Member Consents", False, error="Response not a list")
                    return None
            else:
                self.log_test("Get Member Consents", False, error=f"HTTP {response.status_code if response else 'No response'}")
                return None
                
        except Exception as e:
            self.log_test("Get Member Consents", False, error=str(e))
            return None
    
    def test_multiple_members_risk_patterns(self):
        """Test risk analysis across different member patterns"""
        print("=" * 60)
        print("TESTING RISK PATTERNS ACROSS DIFFERENT MEMBERS")
        print("=" * 60)
        
        risk_results = {}
        
        for pattern, email in TEST_MEMBERS.items():
            print(f"\nTesting {pattern} pattern with {email}...")
            
            # Login as this member
            if self.test_login(email, TEST_PASSWORD):
                member = self.test_get_member_profile()
                if member:
                    member_id = member.get('id')
                    
                    # Get metrics
                    metrics = self.test_get_member_metrics(member_id, days=30)
                    
                    # Analyze risk
                    risk = self.test_analyze_risk(member_id)
                    if risk:
                        risk_tier = risk.get('tier') or risk.get('risk_tier', 'green')
                        explanation = risk.get('explanation_text') or risk.get('explanation', 'No risk detected')
                        risk_results[pattern] = {
                            'member': f"{member.get('first_name')} {member.get('last_name')}",
                            'risk_tier': risk_tier,
                            'explanation': explanation
                        }
        
        # Summary of risk patterns
        print("\n" + "=" * 60)
        print("RISK PATTERN SUMMARY")
        print("=" * 60)
        for pattern, result in risk_results.items():
            risk_tier = result.get('risk_tier', 'unknown')
            if risk_tier:
                print(f"{pattern.upper()}: {result['member']} - {risk_tier.upper()}")
                print(f"  Explanation: {result['explanation'][:100]}...")
                print()
        
        return risk_results
    
    def run_comprehensive_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("AEGIS AI WELLNESS PLATFORM - BACKEND API TESTS")
        print("=" * 60)
        print(f"Base URL: {BASE_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed - aborting tests")
            return False
        
        # Authentication tests
        if not self.test_login():
            print("❌ Login failed - aborting tests")
            return False
        
        self.test_get_current_user()
        self.test_refresh_token()
        
        # Member profile tests
        member = self.test_get_member_profile()
        if not member:
            print("❌ Member profile test failed - aborting member tests")
            return False
        
        member_id = member.get('id')
        self.test_get_member_by_id(member_id)
        
        # Health metrics tests
        self.test_get_member_metrics(member_id, days=7)
        self.test_get_member_metrics(member_id, metric_type='hrv', days=7)
        self.test_get_member_metrics(member_id, days=30)
        
        # Risk analysis tests
        self.test_analyze_risk(member_id)
        self.test_get_current_risk(member_id)
        self.test_get_member_alerts(member_id)
        
        # Device and consent tests
        self.test_get_member_devices(member_id)
        self.test_get_member_consents(member_id)
        
        # Multi-member risk pattern tests
        self.test_multiple_members_risk_patterns()
        
        # Test summary
        self.print_test_summary()
        
        return True
    
    def print_test_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['error']}")
        
        print("=" * 60)


def main():
    """Main test function"""
    tester = AegisAPITester()
    
    try:
        success = tester.run_comprehensive_tests()
        
        # Save results to file
        with open('/app/backend_test_results.json', 'w') as f:
            json.dump(tester.test_results, f, indent=2)
        
        print(f"\nTest results saved to: /app/backend_test_results.json")
        
        # Exit with appropriate code
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()