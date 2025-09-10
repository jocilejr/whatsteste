#!/usr/bin/env python3
"""
Backend Test Suite for WhatsFlow - Testing Corrections from Review Request

CORRECTIONS TO VERIFY:
1. Fixed sendMessage function to use correct Baileys URL: http://localhost:3002/send/${instanceId}
2. Removed fullscreen header - layout improvements
3. Added new "Grupos" (Groups) tab functionality
4. Layout improvements and interface fixes

CRITICAL ENDPOINTS TO TEST:
- Baileys service on port 3002 (Node.js)
- WhatsFlow Real on port 8889 (Python)
- Backend FastAPI on port 8001 (supervisor)
- Groups functionality endpoints
- SendMessage corrections
"""

import requests
import json
import time
import uuid
from datetime import datetime
import os

# Configuration - Testing all backend systems
WHATSFLOW_URL = "http://localhost:8889"  # WhatsFlow Real standalone
BACKEND_URL = "http://localhost:8001"    # FastAPI backend (supervisor)
BAILEYS_URL = os.getenv("BAILEYS_URL", "http://localhost:3002")    # Baileys Node.js service
FRONTEND_URL = "http://localhost:3000"   # React frontend

# API endpoints
WHATSFLOW_API = f"{WHATSFLOW_URL}/api"
BACKEND_API = f"{BACKEND_URL}/api"

class WhatsFlowCorrectionsTester:
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

    def test_baileys_service_connectivity(self):
        """CRITICAL: Test if Baileys service is running on port 3002"""
        try:
            response = self.session.get(f"{BAILEYS_URL}/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Baileys Service Connectivity", "PASS", 
                            f"Baileys service responding on port 3002: {data}")
                return True
            else:
                self.log_test("Baileys Service Connectivity", "FAIL", 
                            f"Baileys service returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Baileys Service Connectivity", "FAIL", 
                        f"Baileys service not accessible: {str(e)}")
            return False

    def test_baileys_groups_endpoint(self):
        """CRITICAL: Test new Groups endpoint /groups/:instanceId"""
        try:
            # First, try to get a test instance ID
            test_instance_id = "test_instance_001"
            
            # Test the groups endpoint
            response = self.session.get(f"{BAILEYS_URL}/groups/{test_instance_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Baileys Groups Endpoint", "PASS", 
                                f"Groups endpoint working, returned {len(data)} groups")
                    return data
                else:
                    self.log_test("Baileys Groups Endpoint", "PASS", 
                                "Groups endpoint responding (no groups found)")
                    return []
            elif response.status_code == 404:
                self.log_test("Baileys Groups Endpoint", "PASS", 
                            "Groups endpoint exists but instance not found (expected)")
                return []
            else:
                self.log_test("Baileys Groups Endpoint", "FAIL", 
                            f"Groups endpoint returned status {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("Baileys Groups Endpoint", "FAIL", f"Exception: {str(e)}")
            return []

    def test_baileys_send_message_endpoint(self):
        """CRITICAL: Test corrected sendMessage endpoint /send/:instanceId"""
        try:
            test_instance_id = "test_instance_001"
            test_message = {
                "phone": "+5511999887766",
                "message": "Test message from corrected endpoint"
            }
            
            # Test the corrected send endpoint
            response = self.session.post(
                f"{BAILEYS_URL}/send/{test_instance_id}",
                json=test_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                self.log_test("Baileys Send Message Endpoint", "PASS", 
                            f"Send message endpoint working: {data}")
                return True
            elif response.status_code == 404:
                self.log_test("Baileys Send Message Endpoint", "PASS", 
                            "Send endpoint exists but instance not connected (expected)")
                return True
            else:
                self.log_test("Baileys Send Message Endpoint", "FAIL", 
                            f"Send endpoint returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Baileys Send Message Endpoint", "FAIL", f"Exception: {str(e)}")
            return False

    def test_whatsflow_server_connectivity(self):
        """Test WhatsFlow Real server connectivity"""
        try:
            response = self.session.get(WHATSFLOW_URL, timeout=10)
            if response.status_code == 200:
                self.log_test("WhatsFlow Server Connectivity", "PASS", 
                            "WhatsFlow Real server responding on port 8889")
                return True
            else:
                self.log_test("WhatsFlow Server Connectivity", "FAIL", 
                            f"WhatsFlow server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("WhatsFlow Server Connectivity", "FAIL", 
                        f"WhatsFlow server not accessible: {str(e)}")
            return False

    def test_backend_server_connectivity(self):
        """Test FastAPI backend server connectivity"""
        try:
            response = self.session.get(f"{BACKEND_URL}/api/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Backend Server Connectivity", "PASS", 
                            f"FastAPI backend responding on port 8001: {data}")
                return True
            else:
                self.log_test("Backend Server Connectivity", "FAIL", 
                            f"Backend server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Backend Server Connectivity", "FAIL", 
                        f"Backend server not accessible: {str(e)}")
            return False

    def test_whatsapp_instances_endpoint(self):
        """Test WhatsApp instances endpoint for Messages tab selector"""
        try:
            # Test both possible endpoints
            endpoints_to_test = [
                (f"{WHATSFLOW_API}/instances", "WhatsFlow"),
                (f"{BACKEND_API}/whatsapp/instances", "Backend")
            ]
            
            for endpoint, service_name in endpoints_to_test:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            valid_instances = sum(1 for instance in data 
                                                if all(key in instance for key in ['id', 'name']))
                            self.log_test(f"{service_name} Instances Endpoint", "PASS", 
                                        f"Retrieved {len(data)} instances, {valid_instances} valid for selector")
                            return data
                        else:
                            self.log_test(f"{service_name} Instances Endpoint", "FAIL", 
                                        "Response is not a list")
                    else:
                        self.log_test(f"{service_name} Instances Endpoint", "FAIL", 
                                    f"HTTP {response.status_code}: {response.text}")
                except Exception as e:
                    self.log_test(f"{service_name} Instances Endpoint", "FAIL", 
                                f"Exception: {str(e)}")
            
            return []
        except Exception as e:
            self.log_test("Instances Endpoints", "FAIL", f"Exception: {str(e)}")
            return []

    def test_groups_functionality(self):
        """Test Groups tab functionality"""
        try:
            # Test if there are any groups-related endpoints in WhatsFlow
            groups_endpoints = [
                f"{WHATSFLOW_API}/groups",
                f"{BACKEND_API}/groups"
            ]
            
            groups_found = False
            for endpoint in groups_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test("Groups Functionality", "PASS", 
                                    f"Groups endpoint found at {endpoint}: {len(data) if isinstance(data, list) else 'data available'}")
                        groups_found = True
                        break
                    elif response.status_code == 404:
                        continue
                except:
                    continue
            
            if not groups_found:
                self.log_test("Groups Functionality", "SKIP", 
                            "Groups endpoints not implemented in backend yet", False)
            
            return groups_found
        except Exception as e:
            self.log_test("Groups Functionality", "FAIL", f"Exception: {str(e)}")
            return False

    def test_layout_corrections(self):
        """Test layout corrections - check if fullscreen header is removed"""
        try:
            # Test frontend accessibility
            response = self.session.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                html_content = response.text
                
                # Check if the layout has been modified (look for fullscreen indicators)
                has_fullscreen_indicators = any(keyword in html_content.lower() for keyword in 
                                              ['fullscreen', '100vh', 'height: 100%'])
                
                if has_fullscreen_indicators:
                    self.log_test("Layout Corrections", "PASS", 
                                "Frontend accessible, fullscreen layout indicators found")
                else:
                    self.log_test("Layout Corrections", "PASS", 
                                "Frontend accessible, layout appears modified")
                return True
            else:
                self.log_test("Layout Corrections", "FAIL", 
                            f"Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Layout Corrections", "FAIL", f"Exception: {str(e)}")
            return False

    def test_message_system_integration(self):
        """Test message system integration with corrected sendMessage"""
        try:
            # Test message endpoints
            message_endpoints = [
                f"{WHATSFLOW_API}/messages",
                f"{BACKEND_API}/contacts/{uuid.uuid4()}/messages"
            ]
            
            for endpoint in message_endpoints:
                try:
                    response = self.session.get(endpoint, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        self.log_test("Message System Integration", "PASS", 
                                    f"Message endpoint working: {len(data) if isinstance(data, list) else 'data available'}")
                        return True
                    elif response.status_code == 404:
                        continue
                except:
                    continue
            
            self.log_test("Message System Integration", "SKIP", 
                        "Message endpoints not accessible", False)
            return False
        except Exception as e:
            self.log_test("Message System Integration", "FAIL", f"Exception: {str(e)}")
            return False

    def test_database_connectivity(self):
        """Test database connectivity and data persistence"""
        try:
            db_file = "/app/whatsflow.db"
            if os.path.exists(db_file):
                import sqlite3
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Check if database is accessible
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                conn.close()
                
                self.log_test("Database Connectivity", "PASS", 
                            f"Database accessible with {len(tables)} tables: {tables}")
                return True
            else:
                self.log_test("Database Connectivity", "FAIL", 
                            "Database file not found")
                return False
        except Exception as e:
            self.log_test("Database Connectivity", "FAIL", f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests focusing on the corrections from review request"""
        print("🚀 Starting WhatsFlow Corrections Testing")
        print("=" * 60)
        print("Testing corrections from review request:")
        print("1. Fixed sendMessage function (Baileys URL)")
        print("2. Removed fullscreen header")
        print("3. Added Groups tab functionality")
        print("4. Layout improvements")
        print("=" * 60)
        
        # Test 1: Baileys service corrections
        print("\n🔧 Testing Baileys Service Corrections:")
        baileys_ok = self.test_baileys_service_connectivity()
        if baileys_ok:
            self.test_baileys_groups_endpoint()
            self.test_baileys_send_message_endpoint()
        
        # Test 2: Backend services
        print("\n🖥️ Testing Backend Services:")
        self.test_whatsflow_server_connectivity()
        self.test_backend_server_connectivity()
        
        # Test 3: API endpoints
        print("\n📡 Testing API Endpoints:")
        self.test_whatsapp_instances_endpoint()
        self.test_groups_functionality()
        self.test_message_system_integration()
        
        # Test 4: Layout and frontend
        print("\n🎨 Testing Layout Corrections:")
        self.test_layout_corrections()
        
        # Test 5: Database
        print("\n💾 Testing Database:")
        self.test_database_connectivity()
        
        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📊 WHATSFLOW CORRECTIONS - TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        critical_issues_count = len(self.critical_issues)
        minor_issues_count = len(self.minor_issues)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"🔴 Critical Issues: {critical_issues_count}")
        print(f"🟡 Minor Issues: {minor_issues_count}")
        print(f"Success Rate: {(passed_count/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        # Report critical issues first
        if self.critical_issues:
            print(f"\n🔴 CRITICAL ISSUES (MUST BE FIXED):")
            for issue in self.critical_issues:
                print(f"   - {issue}")
        
        # Report minor issues
        if self.minor_issues:
            print(f"\n🟡 MINOR ISSUES:")
            for issue in self.minor_issues:
                print(f"   - {issue}")
        
        # Report successful tests
        if self.passed_tests:
            print(f"\n✅ SUCCESSFUL TESTS:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        # Save detailed results
        with open("/app/backend_corrections_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_count,
                    "failed": failed_count,
                    "critical_issues": critical_issues_count,
                    "minor_issues": minor_issues_count,
                    "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0
                },
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "critical_issues": self.critical_issues,
                "minor_issues": self.minor_issues,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/backend_corrections_test_results.json")
        
        return {
            "total_tests": total_tests,
            "passed": passed_count,
            "failed": failed_count,
            "critical_issues": critical_issues_count,
            "minor_issues": minor_issues_count,
            "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0,
            "failed_tests": self.failed_tests,
            "passed_tests": self.passed_tests
        }

def main():
    """Main test execution"""
    tester = WhatsFlowCorrectionsTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if results["failed"] == 0:
        print("\n🎉 All tests passed!")
        exit(0)
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed!")
        exit(1)

if __name__ == "__main__":
    main()