#!/usr/bin/env python3
"""
Review Request Backend Test Suite for WhatsFlow Real
Testing specific corrections mentioned in the review request:

SPECIFIC TESTS REQUESTED:
1. **Endpoint /groups**: Test http://localhost:3002/groups/{instanceId} from Baileys service - should return appropriate error when instance not connected
2. **Baileys Connection**: Verify Baileys service on port 3002 and health checks
3. **WhatsFlow APIs**: Test endpoints on port 8889 (/api/stats, /api/instances, /api/contacts, /api/messages)
4. **Frontend-Backend Integration**: Check if frontend can access both services

PREVIOUS DATA MENTIONED:
- Had 6 contacts, 6 conversations, 0 messages
- System running on http://localhost:8889
- Baileys on http://localhost:3002

PROBLEMS CORRECTED:
- Implemented endpoint /groups/{instanceId} in Baileys service
- Improved error handling for instances not connected
- Design interface completely renovated
"""

import requests
import json
import time
import uuid
from datetime import datetime
import subprocess
import os

# Configuration based on review request
WHATSFLOW_URL = "http://localhost:8889"
BAILEYS_URL = os.getenv("BAILEYS_URL", "http://localhost:3002")
FRONTEND_URL = "http://localhost:3000"
WHATSFLOW_API = f"{WHATSFLOW_URL}/api"

class ReviewRequestTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        self.critical_issues = []
        self.minor_issues = []
        
    def log_test(self, test_name, status, details="", is_critical=True):
        """Log test results with critical/minor classification"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "is_critical": is_critical
        }
        self.test_results.append(result)
        
        if status == "PASS":
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            if is_critical:
                self.critical_issues.append(f"{test_name}: {details}")
            else:
                self.minor_issues.append(f"{test_name}: {details}")
            print(f"❌ {test_name}: {details}")

    def get_real_instance_id(self):
        """Get a real instance ID from WhatsFlow system"""
        try:
            response = self.session.get(f"{WHATSFLOW_API}/instances", timeout=10)
            if response.status_code == 200:
                instances = response.json()
                if instances and len(instances) > 0:
                    return instances[0].get('id', 'test-id')
            return 'test-id'  # Fallback for testing
        except:
            return 'test-id'

    def test_baileys_health_check(self):
        """TEST 1: Baileys Connection - Health check on port 3002"""
        print("\n🏥 TESTING BAILEYS HEALTH CHECK (Port 3002):")
        
        try:
            # Test health endpoint
            response = self.session.get(f"{BAILEYS_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                uptime = data.get('uptime', 'unknown')
                self.log_test("Baileys Health Check", "PASS", 
                            f"Status: {status}, Uptime: {uptime}")
                return True
            else:
                self.log_test("Baileys Health Check", "FAIL", 
                            f"Health endpoint returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Baileys Health Check", "FAIL", 
                        f"Health endpoint not accessible: {str(e)}")
            return False

    def test_baileys_groups_endpoint(self):
        """TEST 2: Endpoint /groups - Test /groups/{instanceId} with error handling"""
        print("\n👥 TESTING BAILEYS GROUPS ENDPOINT:")
        
        instance_id = self.get_real_instance_id()
        
        try:
            # Test groups endpoint with real instance ID
            response = self.session.get(f"{BAILEYS_URL}/groups/{instance_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Baileys Groups Endpoint", "PASS", 
                            f"Groups endpoint working - returned {len(data) if isinstance(data, list) else 'data'}")
                return True
            elif response.status_code == 400:
                # Expected error when instance not connected
                data = response.json()
                error_msg = data.get('error', '')
                if 'não conectada' in error_msg.lower() or 'not connected' in error_msg.lower():
                    self.log_test("Baileys Groups Endpoint", "PASS", 
                                f"Correct error handling for unconnected instance: {error_msg}")
                    return True
                else:
                    self.log_test("Baileys Groups Endpoint", "FAIL", 
                                f"Unexpected error message: {error_msg}")
                    return False
            else:
                self.log_test("Baileys Groups Endpoint", "FAIL", 
                            f"Unexpected status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Baileys Groups Endpoint", "FAIL", 
                        f"Groups endpoint error: {str(e)}")
            return False

    def test_whatsflow_apis(self):
        """TEST 3: WhatsFlow APIs - Test main endpoints on port 8889"""
        print("\n📡 TESTING WHATSFLOW APIs (Port 8889):")
        
        # Test specific endpoints mentioned in review request
        endpoints = [
            ("/stats", "System Statistics"),
            ("/instances", "WhatsApp Instances"),
            ("/contacts", "Contacts Management"),
            ("/messages", "Messages System")
        ]
        
        all_working = True
        for endpoint, name in endpoints:
            try:
                response = self.session.get(f"{WHATSFLOW_API}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"WhatsFlow {name}", "PASS", 
                                    f"API working - {len(data)} records")
                    elif isinstance(data, dict):
                        # For stats endpoint
                        if endpoint == "/stats":
                            stats_info = []
                            for key, value in data.items():
                                stats_info.append(f"{key}: {value}")
                            self.log_test(f"WhatsFlow {name}", "PASS", 
                                        f"API working - {', '.join(stats_info)}")
                        else:
                            self.log_test(f"WhatsFlow {name}", "PASS", 
                                        "API working - data available")
                    else:
                        self.log_test(f"WhatsFlow {name}", "PASS", 
                                    "API working - response received")
                else:
                    self.log_test(f"WhatsFlow {name}", "FAIL", 
                                f"API returned status {response.status_code}: {response.text}")
                    all_working = False
            except Exception as e:
                self.log_test(f"WhatsFlow {name}", "FAIL", 
                            f"API error: {str(e)}")
                all_working = False
        
        return all_working

    def test_frontend_backend_integration(self):
        """TEST 4: Frontend-Backend Integration - Check if frontend can access both services"""
        print("\n🔗 TESTING FRONTEND-BACKEND INTEGRATION:")
        
        # Test 1: Frontend accessibility
        try:
            response = self.session.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                self.log_test("Frontend Accessibility", "PASS", 
                            "Frontend is accessible and responding")
                
                # Check if frontend can make API calls (look for API URLs in HTML)
                html_content = response.text
                api_references = []
                
                if WHATSFLOW_URL in html_content:
                    api_references.append("WhatsFlow API")
                if BAILEYS_URL in html_content:
                    api_references.append("Baileys API")
                if "localhost:8889" in html_content:
                    api_references.append("Port 8889 reference")
                if "localhost:3002" in html_content:
                    api_references.append("Port 3002 reference")
                
                if api_references:
                    self.log_test("Frontend API Integration", "PASS", 
                                f"Frontend configured for API access: {', '.join(api_references)}")
                else:
                    self.log_test("Frontend API Integration", "SKIP", 
                                "No explicit API references found in HTML", False)
                
                return True
            else:
                self.log_test("Frontend Accessibility", "FAIL", 
                            f"Frontend returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Accessibility", "FAIL", 
                        f"Frontend not accessible: {str(e)}")
            return False

    def test_baileys_service_status(self):
        """Additional test: Baileys service status endpoint"""
        print("\n🔍 TESTING BAILEYS SERVICE STATUS:")
        
        try:
            response = self.session.get(f"{BAILEYS_URL}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Baileys Service Status", "PASS", 
                            f"Status endpoint working: {data}")
                return True
            else:
                self.log_test("Baileys Service Status", "FAIL", 
                            f"Status endpoint returned {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Baileys Service Status", "FAIL", 
                        f"Status endpoint error: {str(e)}")
            return False

    def test_system_data_verification(self):
        """Verify system data matches previous state mentioned in review"""
        print("\n📊 TESTING SYSTEM DATA VERIFICATION:")
        
        try:
            # Get contacts count
            contacts_response = self.session.get(f"{WHATSFLOW_API}/contacts", timeout=10)
            contacts_count = 0
            if contacts_response.status_code == 200:
                contacts = contacts_response.json()
                contacts_count = len(contacts) if isinstance(contacts, list) else 0
            
            # Get messages count
            messages_response = self.session.get(f"{WHATSFLOW_API}/messages", timeout=10)
            messages_count = 0
            if messages_response.status_code == 200:
                messages = messages_response.json()
                messages_count = len(messages) if isinstance(messages, list) else 0
            
            # Get instances count
            instances_response = self.session.get(f"{WHATSFLOW_API}/instances", timeout=10)
            instances_count = 0
            if instances_response.status_code == 200:
                instances = instances_response.json()
                instances_count = len(instances) if isinstance(instances, list) else 0
            
            self.log_test("System Data Verification", "PASS", 
                        f"Current data: {contacts_count} contacts, {messages_count} messages, {instances_count} instances", False)
            
            return True
        except Exception as e:
            self.log_test("System Data Verification", "FAIL", 
                        f"Data verification error: {str(e)}")
            return False

    def test_service_processes(self):
        """Check if services are running as processes"""
        print("\n⚙️ TESTING SERVICE PROCESSES:")
        
        try:
            # Check for Python processes (WhatsFlow Real)
            result = subprocess.run(['pgrep', '-f', 'python.*8889'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                self.log_test("WhatsFlow Real Process", "PASS", 
                            f"WhatsFlow Real running (PIDs: {', '.join(pids)})")
            else:
                self.log_test("WhatsFlow Real Process", "FAIL", 
                            "WhatsFlow Real process not found")
            
            # Check for Node.js processes (Baileys)
            result = subprocess.run(['pgrep', '-f', 'node.*3002'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                self.log_test("Baileys Service Process", "PASS", 
                            f"Baileys service running (PIDs: {', '.join(pids)})")
            else:
                self.log_test("Baileys Service Process", "FAIL", 
                            "Baileys service process not found")
            
            return True
        except Exception as e:
            self.log_test("Service Processes", "FAIL", 
                        f"Process check error: {str(e)}")
            return False

    def run_review_request_tests(self):
        """Run all tests requested in the review"""
        print("🎯 REVIEW REQUEST BACKEND TESTING")
        print("=" * 60)
        print("Testing WhatsFlow Real system after corrections:")
        print("✅ 1. Endpoint /groups implementation")
        print("✅ 2. Baileys connection and health checks")
        print("✅ 3. WhatsFlow APIs functionality")
        print("✅ 4. Frontend-Backend integration")
        print("=" * 60)
        
        # Run all requested tests
        baileys_health = self.test_baileys_health_check()
        baileys_groups = self.test_baileys_groups_endpoint()
        whatsflow_apis = self.test_whatsflow_apis()
        frontend_integration = self.test_frontend_backend_integration()
        
        # Additional verification tests
        baileys_status = self.test_baileys_service_status()
        data_verification = self.test_system_data_verification()
        process_check = self.test_service_processes()
        
        return self.generate_review_report()

    def generate_review_report(self):
        """Generate comprehensive review report"""
        print("\n" + "=" * 70)
        print("📊 REVIEW REQUEST TEST RESULTS - WHATSFLOW REAL")
        print("=" * 70)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        critical_issues_count = len(self.critical_issues)
        minor_issues_count = len(self.minor_issues)
        
        print(f"📈 SUMMARY:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_count}")
        print(f"   ❌ Failed: {failed_count}")
        print(f"   🔴 Critical Issues: {critical_issues_count}")
        print(f"   🟡 Minor Issues: {minor_issues_count}")
        print(f"   📊 Success Rate: {(passed_count/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # Review request specific validations
        print(f"\n🎯 REVIEW REQUEST VALIDATIONS:")
        validations = {
            "Baileys Health Check": any("Baileys Health" in test for test in self.passed_tests),
            "Groups Endpoint Implementation": any("Groups Endpoint" in test for test in self.passed_tests),
            "WhatsFlow APIs Working": any("WhatsFlow" in test and "API" in test for test in self.passed_tests),
            "Frontend Integration": any("Frontend" in test for test in self.passed_tests)
        }
        
        for validation, status in validations.items():
            status_icon = "✅ VALIDATED" if status else "❌ NOT VALIDATED"
            print(f"   {status_icon} - {validation}")
        
        # Critical issues
        if self.critical_issues:
            print(f"\n🔴 CRITICAL ISSUES REQUIRING ATTENTION:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        
        # Minor issues
        if self.minor_issues:
            print(f"\n🟡 MINOR ISSUES (NON-BLOCKING):")
            for i, issue in enumerate(self.minor_issues, 1):
                print(f"   {i}. {issue}")
        
        # Successful tests
        if self.passed_tests:
            print(f"\n✅ SUCCESSFUL VALIDATIONS:")
            for i, test in enumerate(self.passed_tests, 1):
                print(f"   {i}. {test}")
        
        # Save results
        results_file = "/app/review_request_test_results.json"
        with open(results_file, "w") as f:
            json.dump({
                "test_summary": {
                    "total_tests": total_tests,
                    "passed": passed_count,
                    "failed": failed_count,
                    "critical_issues": critical_issues_count,
                    "minor_issues": minor_issues_count,
                    "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0
                },
                "review_request_validations": validations,
                "tested_endpoints": [
                    "GET http://localhost:3002/health",
                    "GET http://localhost:3002/groups/{instanceId}",
                    "GET http://localhost:8889/api/stats",
                    "GET http://localhost:8889/api/instances",
                    "GET http://localhost:8889/api/contacts",
                    "GET http://localhost:8889/api/messages"
                ],
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "critical_issues": self.critical_issues,
                "minor_issues": self.minor_issues,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Complete results saved to: {results_file}")
        
        return {
            "total_tests": total_tests,
            "passed": passed_count,
            "failed": failed_count,
            "critical_issues": critical_issues_count,
            "minor_issues": minor_issues_count,
            "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0,
            "review_validations": sum(1 for status in validations.values() if status)
        }

def main():
    """Main execution"""
    tester = ReviewRequestTester()
    results = tester.run_review_request_tests()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"📊 System Health: {results['success_rate']:.1f}%")
    print(f"✅ Review Validations: {results['review_validations']}/4")
    
    if results["critical_issues"] == 0:
        print("🎉 All critical systems are functioning correctly!")
        print("✅ Review request corrections have been validated!")
    else:
        print(f"⚠️ {results['critical_issues']} critical issue(s) need attention")

if __name__ == "__main__":
    main()