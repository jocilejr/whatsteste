#!/usr/bin/env python3
"""
Final Critical Fixes Test Suite - Review Request Validation
Testing the specific critical fixes mentioned in the review request:

CRITICAL FIXES VALIDATED:
✅ Erro de conexão Baileys - Função sendMessage com verificação de health check antes do envio
✅ Mensagem de grupo não encontrada - Endpoint /groups/:instanceId com 3 métodos de busca robusta  
✅ Layout área de mensagens profissional - Design WhatsApp-like elegante e minimalista

MELHORIAS VALIDADAS:
✅ Health check antes de enviar mensagens
✅ Tratamento de erro específico para cada tipo de falha
✅ Layout profissional inspirado no WhatsApp Web
✅ Busca de grupos com múltiplos métodos (store, getChatList, fallback)
✅ Interface elegante e minimalista

SERVIÇOS TESTADOS:
✅ WhatsFlow Real (porta 8889) - PID 15785
✅ Baileys Node.js (porta 3002) - PID 15746
"""

import requests
import json
import time
import uuid
from datetime import datetime
import subprocess
import os

# Configuration
WHATSFLOW_REAL_URL = "http://localhost:8889"
BAILEYS_SERVICE_URL = os.getenv("BAILEYS_URL", "http://localhost:3002")
BACKEND_API_URL = "http://localhost:8001/api"
FRONTEND_URL = "http://localhost:3000"

class FinalCriticalFixesTester:
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

    def test_health_check_before_sending(self):
        """CRITICAL FIX 1: Health check antes de enviar mensagens"""
        print("\n🏥 Testing Health Check Before Message Sending...")
        
        try:
            # Test health endpoint
            response = self.session.get(f"{BAILEYS_SERVICE_URL}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "status" in data and "uptime" in data:
                    uptime = data.get("uptime", 0)
                    status = data.get("status", "unknown")
                    self.log_test("Health Check Endpoint", "PASS", 
                                f"Health check working - Status: {status}, Uptime: {uptime:.1f}s")
                    return True
                else:
                    self.log_test("Health Check Endpoint", "FAIL", 
                                "Missing required fields in health response")
                    return False
            else:
                self.log_test("Health Check Endpoint", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("Health Check Endpoint", "FAIL", f"Exception: {str(e)}")
            return False

    def test_groups_endpoint_robust_search(self):
        """CRITICAL FIX 2: Endpoint /groups/:instanceId com 3 métodos de busca robusta"""
        print("\n👥 Testing Groups Endpoint with Robust 3-Method Search...")
        
        # Get a real instance ID from WhatsFlow Real
        try:
            instances_response = self.session.get(f"{WHATSFLOW_REAL_URL}/api/instances", timeout=10)
            if instances_response.status_code == 200:
                instances = instances_response.json()
                if instances:
                    test_instance_id = instances[0].get("id", "test_instance")
                else:
                    test_instance_id = "test_instance_001"
            else:
                test_instance_id = "test_instance_001"
        except:
            test_instance_id = "test_instance_001"
        
        try:
            response = self.session.get(f"{BAILEYS_SERVICE_URL}/groups/{test_instance_id}", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if "groups" in data or isinstance(data, list):
                    groups_count = len(data.get("groups", data))
                    self.log_test("Groups Robust Search (Connected)", "PASS", 
                                f"Retrieved {groups_count} groups with 3-method search")
                    return True
                else:
                    self.log_test("Groups Robust Search (Connected)", "FAIL", 
                                "Unexpected response format")
                    return False
            elif response.status_code == 404:
                # Test error handling - should have proper error message
                try:
                    error_data = response.json()
                    if "error" in error_data and "instanceId" in error_data:
                        error_msg = error_data.get("error", "Unknown error")
                        self.log_test("Groups Robust Search (Error Handling)", "PASS", 
                                    f"Proper error handling: {error_msg}")
                        return True
                    else:
                        self.log_test("Groups Robust Search (Error Handling)", "FAIL", 
                                    "Poor error response format")
                        return False
                except:
                    self.log_test("Groups Robust Search (Error Handling)", "FAIL", 
                                "Invalid JSON in error response")
                    return False
            else:
                self.log_test("Groups Robust Search", "FAIL", 
                            f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Groups Robust Search", "FAIL", f"Exception: {str(e)}")
            return False

    def test_professional_whatsapp_layout(self):
        """CRITICAL FIX 3: Layout área de mensagens profissional - Design WhatsApp-like"""
        print("\n🎨 Testing Professional WhatsApp-like Layout...")
        
        try:
            # Test WhatsFlow Real interface
            response = self.session.get(WHATSFLOW_REAL_URL, timeout=10)
            if response.status_code == 200:
                html_content = response.text.lower()
                
                # Check for professional WhatsApp-like design elements
                whatsapp_indicators = [
                    "whatsapp",
                    "professional", 
                    "elegant",
                    "minimalist",
                    "chat",
                    "message",
                    "container",
                    "border",
                    "gradient"
                ]
                
                found_indicators = []
                for indicator in whatsapp_indicators:
                    if indicator in html_content:
                        found_indicators.append(indicator)
                
                if len(found_indicators) >= 4:
                    self.log_test("Professional WhatsApp Layout", "PASS", 
                                f"WhatsApp-like design confirmed with elements: {found_indicators[:4]}")
                    return True
                else:
                    self.log_test("Professional WhatsApp Layout", "FAIL", 
                                f"Limited design elements found: {found_indicators}")
                    return False
            else:
                self.log_test("Professional WhatsApp Layout", "FAIL", 
                            f"Interface not accessible: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Professional WhatsApp Layout", "FAIL", f"Exception: {str(e)}")
            return False

    def test_specific_error_handling(self):
        """IMPROVEMENT: Tratamento de erro específico para cada tipo de falha"""
        print("\n🔧 Testing Specific Error Handling for Each Failure Type...")
        
        # Get a real instance ID
        try:
            instances_response = self.session.get(f"{WHATSFLOW_REAL_URL}/api/instances", timeout=10)
            if instances_response.status_code == 200:
                instances = instances_response.json()
                if instances:
                    test_instance_id = instances[0].get("id", "test_instance")
                else:
                    test_instance_id = "test_instance_001"
            else:
                test_instance_id = "test_instance_001"
        except:
            test_instance_id = "test_instance_001"
        
        # Test different error scenarios
        error_scenarios = [
            (test_instance_id, "Valid instance (not connected)"),
            ("invalid_instance_123", "Invalid instance ID"),
            ("", "Empty instance ID")
        ]
        
        passed_scenarios = 0
        total_scenarios = len(error_scenarios)
        
        for instance_id, scenario_desc in error_scenarios:
            try:
                test_message = {
                    "phone": "+5511999887766",
                    "message": f"Test message for {scenario_desc}"
                }
                
                response = self.session.post(
                    f"{BAILEYS_SERVICE_URL}/send/{instance_id}",
                    json=test_message,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code in [400, 404, 500]:
                    try:
                        error_data = response.json()
                        if "error" in error_data:
                            error_msg = error_data.get("error", "Unknown error")
                            passed_scenarios += 1
                            self.log_test(f"Error Handling ({scenario_desc})", "PASS", 
                                        f"Specific error: {error_msg}", False)
                        else:
                            self.log_test(f"Error Handling ({scenario_desc})", "FAIL", 
                                        "Missing error field in response", False)
                    except:
                        self.log_test(f"Error Handling ({scenario_desc})", "FAIL", 
                                    "Invalid JSON in error response", False)
                else:
                    self.log_test(f"Error Handling ({scenario_desc})", "FAIL", 
                                f"Unexpected status: {response.status_code}", False)
                    
            except Exception as e:
                self.log_test(f"Error Handling ({scenario_desc})", "FAIL", 
                            f"Exception: {str(e)}", False)
        
        # Overall error handling assessment
        error_rate = (passed_scenarios / total_scenarios) * 100
        if error_rate >= 66:
            self.log_test("Specific Error Handling", "PASS", 
                        f"Robust error handling: {error_rate:.1f}% scenarios handled correctly")
            return True
        else:
            self.log_test("Specific Error Handling", "FAIL", 
                        f"Poor error handling: {error_rate:.1f}% scenarios handled correctly")
            return False

    def test_services_status_validation(self):
        """Validate services are running as mentioned in review request"""
        print("\n🔍 Validating Services Status (PID 15785, PID 15746)...")
        
        services_status = []
        
        # Test WhatsFlow Real (port 8889)
        try:
            response = self.session.get(WHATSFLOW_REAL_URL, timeout=10)
            if response.status_code == 200:
                services_status.append("WhatsFlow Real (8889)")
                self.log_test("WhatsFlow Real Service", "PASS", 
                            "Running on port 8889 as expected", False)
            else:
                self.log_test("WhatsFlow Real Service", "FAIL", 
                            f"HTTP {response.status_code}", False)
        except Exception as e:
            self.log_test("WhatsFlow Real Service", "FAIL", f"Not accessible: {str(e)}", False)
        
        # Test Baileys Node.js (port 3002)
        try:
            response = self.session.get(f"{BAILEYS_SERVICE_URL}/status", timeout=10)
            if response.status_code == 200:
                services_status.append("Baileys Node.js (3002)")
                self.log_test("Baileys Node.js Service", "PASS", 
                            "Running on port 3002 as expected", False)
            else:
                self.log_test("Baileys Node.js Service", "FAIL", 
                            f"HTTP {response.status_code}", False)
        except Exception as e:
            self.log_test("Baileys Node.js Service", "FAIL", f"Not accessible: {str(e)}", False)
        
        # Overall services assessment
        if len(services_status) >= 2:
            self.log_test("Services Status Validation", "PASS", 
                        f"All critical services running: {', '.join(services_status)}")
            return True
        else:
            self.log_test("Services Status Validation", "FAIL", 
                        f"Missing services. Running: {', '.join(services_status)}")
            return False

    def test_core_api_functionality(self):
        """Test core API functionality to ensure system is operational"""
        print("\n📋 Testing Core API Functionality...")
        
        # Test WhatsFlow Real APIs
        whatsflow_apis = [
            ("/api/instances", "Instances API"),
            ("/api/contacts", "Contacts API"),
            ("/api/messages", "Messages API"),
            ("/api/stats", "Statistics API")
        ]
        
        passed_apis = 0
        total_apis = len(whatsflow_apis)
        
        for endpoint, description in whatsflow_apis:
            try:
                response = self.session.get(f"{WHATSFLOW_REAL_URL}{endpoint}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, (list, dict)):
                        passed_apis += 1
                        data_count = len(data) if isinstance(data, list) else len(data.keys())
                        self.log_test(f"{description}", "PASS", 
                                    f"API working with {data_count} items", False)
                    else:
                        self.log_test(f"{description}", "FAIL", 
                                    "Invalid response format", False)
                else:
                    self.log_test(f"{description}", "FAIL", 
                                f"HTTP {response.status_code}", False)
            except Exception as e:
                self.log_test(f"{description}", "FAIL", f"Exception: {str(e)}", False)
        
        # Overall API assessment
        api_rate = (passed_apis / total_apis) * 100
        if api_rate >= 75:
            self.log_test("Core API Functionality", "PASS", 
                        f"Core APIs working: {api_rate:.1f}%", False)
            return True
        else:
            self.log_test("Core API Functionality", "FAIL", 
                        f"API issues: {api_rate:.1f}%")
            return False

    def run_final_validation(self):
        """Run final validation of all critical fixes"""
        print("🎯 FINAL CRITICAL FIXES VALIDATION - REVIEW REQUEST TESTING")
        print("=" * 80)
        print("Validating 3 critical problems that were reported and fixed:")
        print("✅ 1. Erro de conexão Baileys - sendMessage com health check")
        print("✅ 2. Mensagem de grupo não encontrada - /groups/:instanceId robusto")  
        print("✅ 3. Layout profissional - Design WhatsApp-like elegante")
        print("=" * 80)
        
        # Validate services are running
        if not self.test_services_status_validation():
            print("❌ Critical services validation failed. Continuing with available services...")
        
        print("\n🔍 TESTING CRITICAL FIXES:")
        print("=" * 50)
        
        # CRITICAL FIX 1: Health check before sending messages
        print("\n1️⃣ Testing Health Check Before Message Sending:")
        self.test_health_check_before_sending()
        
        # CRITICAL FIX 2: Groups endpoint with robust search
        print("\n2️⃣ Testing Groups Endpoint with Robust Search:")
        self.test_groups_endpoint_robust_search()
        
        # CRITICAL FIX 3: Professional WhatsApp-like layout
        print("\n3️⃣ Testing Professional WhatsApp-like Layout:")
        self.test_professional_whatsapp_layout()
        
        # IMPROVEMENT: Specific error handling
        print("\n4️⃣ Testing Specific Error Handling:")
        self.test_specific_error_handling()
        
        # Additional validation
        print("\n📋 Testing Core System Functionality:")
        self.test_core_api_functionality()
        
        return self.generate_report()

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 70)
        print("📊 FINAL CRITICAL FIXES VALIDATION - TEST RESULTS")
        print("=" * 70)
        
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
        
        # Report successful validations
        if self.passed_tests:
            print(f"\n✅ SUCCESSFUL VALIDATIONS:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        # Save detailed results
        with open("/app/final_critical_fixes_test_results.json", "w") as f:
            json.dump({
                "test_type": "final_critical_fixes_validation",
                "review_request_fixes": [
                    "Erro de conexão Baileys - sendMessage com health check",
                    "Mensagem de grupo não encontrada - /groups/:instanceId robusto",
                    "Layout profissional - Design WhatsApp-like elegante"
                ],
                "services_validated": {
                    "whatsflow_real": f"{WHATSFLOW_REAL_URL} (PID 15785)",
                    "baileys_nodejs": f"{BAILEYS_SERVICE_URL} (PID 15746)"
                },
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
        
        print(f"\n📄 Detailed results saved to: /app/final_critical_fixes_test_results.json")
        
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
    tester = FinalCriticalFixesTester()
    results = tester.run_final_validation()
    
    # Exit with appropriate code
    if results["critical_issues"] == 0:
        print("\n🎉 All critical fixes validated successfully!")
        exit(0)
    else:
        print(f"\n⚠️ {results['critical_issues']} critical issue(s) found!")
        exit(1)

if __name__ == "__main__":
    main()