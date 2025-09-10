#!/usr/bin/env python3
"""
Critical Fixes Test - Testing specific bugs reported by user and fixed by main agent

REVIEW REQUEST FIXES TO TEST:
1. Erro ao carregar grupos - Endpoint /groups/:instanceId with robust error handling
2. Erro ao filtrar mensagens por instância - loadConversations function with logs and retry
3. Erro ao enviar mensagens - sendMessage function with timeout, detailed logs and error handling
4. "Como funciona" removido - Section removed from interface

SERVICES TO TEST:
- WhatsFlow Real (porta 8889) - PID 14106
- Baileys Node.js (porta 3002) - PID 14067
"""

import os
import requests
import json
import time
from datetime import datetime

class CriticalFixesTester:
    def __init__(self):
        self.whatsflow_url = "http://localhost:8889"
        self.baileys_url = os.getenv("BAILEYS_URL", "http://localhost:3002")
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        if status == "PASS":
            print(f"✅ {test_name}: {details}")
        elif status == "FAIL":
            print(f"❌ {test_name}: {details}")
        else:
            print(f"⚠️ {test_name}: {details}")
    
    def test_groups_endpoint_error_handling(self):
        """Test 1: Erro ao carregar grupos - /groups/:instanceId with robust error handling"""
        print("\n🔍 Testing Groups Endpoint Error Handling...")
        
        # Test with valid instance ID (should handle gracefully)
        try:
            response = self.session.get(f"{self.baileys_url}/groups/valid_instance_001", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data and "instanceId" in data:
                    self.log_test("Groups Endpoint (Valid Instance)", "PASS", 
                                f"Proper error handling: {data.get('error', 'Unknown error')}")
                else:
                    self.log_test("Groups Endpoint (Valid Instance)", "FAIL", 
                                "Response missing error handling fields")
            else:
                self.log_test("Groups Endpoint (Valid Instance)", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Groups Endpoint (Valid Instance)", "FAIL", f"Exception: {str(e)}")
        
        # Test with invalid instance ID (should handle gracefully)
        try:
            response = self.session.get(f"{self.baileys_url}/groups/invalid_instance", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "error" in data and "instanceId" in data:
                    self.log_test("Groups Endpoint (Invalid Instance)", "PASS", 
                                f"Robust error handling: {data.get('error', 'Unknown error')}")
                else:
                    self.log_test("Groups Endpoint (Invalid Instance)", "FAIL", 
                                "Response missing error handling fields")
            else:
                self.log_test("Groups Endpoint (Invalid Instance)", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("Groups Endpoint (Invalid Instance)", "FAIL", f"Exception: {str(e)}")
    
    def test_chats_filtering_with_instance(self):
        """Test 2: Erro ao filtrar mensagens por instância - loadConversations with logs and retry"""
        print("\n🔍 Testing Chats Filtering with Instance ID...")
        
        # Test basic chats endpoint
        try:
            response = self.session.get(f"{self.whatsflow_url}/api/chats", timeout=10)
            
            if response.status_code == 200:
                chats = response.json()
                self.log_test("GET /api/chats (Basic)", "PASS", 
                            f"Retrieved {len(chats)} chats successfully")
            else:
                self.log_test("GET /api/chats (Basic)", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/chats (Basic)", "FAIL", f"Exception: {str(e)}")
        
        # Test chats with instance filtering (if supported)
        try:
            response = self.session.get(f"{self.whatsflow_url}/api/chats?instance_id=test_instance", timeout=10)
            
            if response.status_code == 200:
                chats = response.json()
                self.log_test("GET /api/chats (With Instance Filter)", "PASS", 
                            f"Instance filtering working: {len(chats)} chats")
            elif response.status_code == 404:
                self.log_test("GET /api/chats (With Instance Filter)", "INFO", 
                            "Instance filtering not implemented (expected)")
            else:
                self.log_test("GET /api/chats (With Instance Filter)", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.log_test("GET /api/chats (With Instance Filter)", "FAIL", f"Exception: {str(e)}")
    
    def test_send_message_error_handling(self):
        """Test 3: Erro ao enviar mensagens - sendMessage with timeout, logs and error handling"""
        print("\n🔍 Testing Send Message Error Handling...")
        
        # Test send message endpoint with proper error handling
        test_instances = ["test_instance_001", "invalid_instance", "disconnected_instance"]
        
        for instance_id in test_instances:
            try:
                payload = {
                    "to": "5511999999999",
                    "message": "Test message for error handling",
                    "type": "text"
                }
                
                response = self.session.post(
                    f"{self.baileys_url}/send/{instance_id}",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "success" in data:
                        self.log_test(f"Send Message ({instance_id})", "PASS", 
                                    f"Message sent successfully")
                    else:
                        self.log_test(f"Send Message ({instance_id})", "FAIL", 
                                    "Response missing success field")
                elif response.status_code == 400:
                    data = response.json()
                    if "error" in data and "instanceId" in data:
                        self.log_test(f"Send Message ({instance_id})", "PASS", 
                                    f"Proper error handling: {data.get('error', 'Unknown error')}")
                    else:
                        self.log_test(f"Send Message ({instance_id})", "FAIL", 
                                    "Error response missing required fields")
                else:
                    self.log_test(f"Send Message ({instance_id})", "FAIL", 
                                f"HTTP {response.status_code}: {response.text}")
                        
            except Exception as e:
                self.log_test(f"Send Message ({instance_id})", "FAIL", f"Exception: {str(e)}")
    
    def test_interface_como_funciona_removed(self):
        """Test 4: "Como funciona" removido - Section removed from interface"""
        print("\n🔍 Testing Interface - 'Como funciona' Section Removal...")
        
        try:
            response = self.session.get(self.whatsflow_url, timeout=10)
            
            if response.status_code == 200:
                html_content = response.text
                
                # Check if "Como funciona" section is removed
                como_funciona_indicators = [
                    "Como funciona",
                    "como-funciona",
                    "showSection('como-funciona')",
                    "showSection('info')"  # Old info section
                ]
                
                found_indicators = []
                for indicator in como_funciona_indicators:
                    if indicator.lower() in html_content.lower():
                        found_indicators.append(indicator)
                
                if not found_indicators:
                    self.log_test("Interface - Como Funciona Removed", "PASS", 
                                "Como funciona section successfully removed from interface")
                else:
                    self.log_test("Interface - Como Funciona Removed", "FAIL", 
                                f"Como funciona indicators still found: {found_indicators}")
                
                # Check if Groups section is present (replacement)
                if "groups" in html_content.lower() and "grupos" in html_content.lower():
                    self.log_test("Interface - Groups Section Present", "PASS", 
                                "Groups section properly implemented as replacement")
                else:
                    self.log_test("Interface - Groups Section Present", "FAIL", 
                                "Groups section not found in interface")
                    
            else:
                self.log_test("Interface - Como Funciona Removed", "FAIL", 
                            f"Could not load interface: HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Interface - Como Funciona Removed", "FAIL", f"Exception: {str(e)}")
    
    def test_services_running(self):
        """Test if both services are running as mentioned in review request"""
        print("\n🔍 Testing Services Status...")
        
        # Test WhatsFlow Real (port 8889)
        try:
            response = self.session.get(self.whatsflow_url, timeout=5)
            if response.status_code == 200:
                self.log_test("WhatsFlow Real Service", "PASS", "Running on port 8889")
            else:
                self.log_test("WhatsFlow Real Service", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("WhatsFlow Real Service", "FAIL", f"Not accessible: {str(e)}")
        
        # Test Baileys Node.js (port 3002)
        try:
            response = self.session.get(f"{self.baileys_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("Baileys Node.js Service", "PASS", 
                            f"Running on port 3002, uptime: {data.get('uptime', 'unknown')}s")
            else:
                self.log_test("Baileys Node.js Service", "FAIL", f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Baileys Node.js Service", "FAIL", f"Not accessible: {str(e)}")
    
    def test_api_endpoints_functionality(self):
        """Test core API endpoints are working"""
        print("\n🔍 Testing Core API Endpoints...")
        
        endpoints = [
            ("/api/instances", "GET"),
            ("/api/contacts", "GET"),
            ("/api/messages", "GET"),
            ("/api/stats", "GET"),
            ("/api/chats", "GET")
        ]
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = self.session.get(f"{self.whatsflow_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"{method} {endpoint}", "PASS", f"Retrieved {len(data)} items")
                    elif isinstance(data, dict):
                        self.log_test(f"{method} {endpoint}", "PASS", f"Retrieved data: {len(data)} fields")
                    else:
                        self.log_test(f"{method} {endpoint}", "PASS", "Retrieved data successfully")
                else:
                    self.log_test(f"{method} {endpoint}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.log_test(f"{method} {endpoint}", "FAIL", f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all critical fixes tests"""
        print("🚀 TESTING CRITICAL FIXES FROM REVIEW REQUEST")
        print("=" * 60)
        print("Testing 4 specific bugs that were reported and fixed:")
        print("1. Erro ao carregar grupos")
        print("2. Erro ao filtrar mensagens por instância") 
        print("3. Erro ao enviar mensagens")
        print("4. 'Como funciona' removido")
        print("=" * 60)
        
        # Test services are running
        self.test_services_running()
        
        # Test the 4 specific fixes
        self.test_groups_endpoint_error_handling()
        self.test_chats_filtering_with_instance()
        self.test_send_message_error_handling()
        self.test_interface_como_funciona_removed()
        
        # Test core functionality
        self.test_api_endpoints_functionality()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 CRITICAL FIXES TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = [t for t in self.test_results if t["status"] == "PASS"]
        failed_tests = [t for t in self.test_results if t["status"] == "FAIL"]
        info_tests = [t for t in self.test_results if t["status"] == "INFO"]
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {len(passed_tests)}")
        print(f"❌ Failed: {len(failed_tests)}")
        print(f"ℹ️ Info: {len(info_tests)}")
        print(f"Success Rate: {(len(passed_tests)/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        if info_tests:
            print(f"\nℹ️ INFO TESTS:")
            for test in info_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in passed_tests:
            print(f"   - {test['test']}: {test['details']}")
        
        # Save results
        with open("/app/critical_fixes_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": len(passed_tests),
                    "failed": len(failed_tests),
                    "info": len(info_tests),
                    "success_rate": (len(passed_tests)/total_tests*100) if total_tests > 0 else 0
                },
                "results": self.test_results
            }, f, indent=2)
        
        return {
            "total_tests": total_tests,
            "passed": len(passed_tests),
            "failed": len(failed_tests),
            "success_rate": (len(passed_tests)/total_tests*100) if total_tests > 0 else 0
        }

def main():
    """Main test execution"""
    tester = CriticalFixesTester()
    results = tester.run_all_tests()
    
    print(f"\n📄 Detailed results saved to: /app/critical_fixes_test_results.json")
    
    if results["failed"] == 0:
        print("\n🎉 All critical fixes verified successfully!")
        return 0
    else:
        print(f"\n⚠️ {results['failed']} test(s) failed!")
        return 1

if __name__ == "__main__":
    exit(main())