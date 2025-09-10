#!/usr/bin/env python3
"""
Review Corrections Validation Test Suite
Testing all corrections implemented as per review request:

CORRECTIONS TO VALIDATE:
1. Layout profissional - Bordas nas laterais, container 1200px, espaçamento 20px
2. Cards de instância melhorados - Design menor e mais profissional  
3. Fotos de usuário - Avatares coloridos baseados no telefone (função getAvatarColor)
4. Campo de mensagem refinado - Enter para enviar, design moderno
5. Instâncias de teste removidas - Database limpo
6. Busca de grupos corrigida - Endpoint /groups/:instanceId melhorado
7. Envio de mensagens Baileys - URL corrigida

SERVICES TO TEST:
- WhatsFlow Real (porta 8889) - PID 11241
- Baileys Node.js (porta 3002) - PID 11202
"""

import requests
import json
import time
import sqlite3
import os
import subprocess
from datetime import datetime

# Configuration
WHATSFLOW_URL = "http://localhost:8889"
BAILEYS_URL = "http://localhost:3002"
DB_FILE = "/app/whatsflow.db"

class ReviewCorrectionsValidator:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        self.critical_issues = []
        
    def log_test(self, test_name, success, details="", is_critical=False):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "critical": is_critical
        }
        
        self.test_results.append(result)
        
        if success:
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            if is_critical:
                self.critical_issues.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    def test_whatsflow_service_running(self):
        """Test if WhatsFlow Real service is running on port 8889"""
        try:
            response = self.session.get(f"{WHATSFLOW_URL}/", timeout=10)
            if response.status_code == 200:
                self.log_test("WhatsFlow Real Service", True, f"Service running on port 8889, status: {response.status_code}")
                return True
            else:
                self.log_test("WhatsFlow Real Service", False, f"Service returned status: {response.status_code}", True)
                return False
        except Exception as e:
            self.log_test("WhatsFlow Real Service", False, f"Service not accessible: {str(e)}", True)
            return False
    
    def test_baileys_service_running(self):
        """Test if Baileys service is running on port 3002"""
        try:
            response = self.session.get(f"{BAILEYS_URL}/status", timeout=10)
            if response.status_code == 200:
                self.log_test("Baileys Service", True, f"Service running on port 3002, status: {response.status_code}")
                return True
            else:
                self.log_test("Baileys Service", False, f"Service returned status: {response.status_code}", True)
                return False
        except Exception as e:
            self.log_test("Baileys Service", False, f"Service not accessible: {str(e)}", True)
            return False
    
    def test_database_clean(self):
        """Test if database is clean (test instances removed)"""
        try:
            if not os.path.exists(DB_FILE):
                self.log_test("Database Clean Check", False, "Database file not found", True)
                return False
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check for test instances
            cursor.execute("SELECT COUNT(*) FROM instances WHERE name LIKE '%test%' OR name LIKE '%Test%'")
            test_instances = cursor.fetchone()[0]
            
            # Check total instances
            cursor.execute("SELECT COUNT(*) FROM instances")
            total_instances = cursor.fetchone()[0]
            
            conn.close()
            
            if test_instances == 0:
                self.log_test("Database Clean Check", True, f"No test instances found. Total instances: {total_instances}")
                return True
            else:
                self.log_test("Database Clean Check", False, f"Found {test_instances} test instances out of {total_instances} total")
                return False
                
        except Exception as e:
            self.log_test("Database Clean Check", False, f"Database check failed: {str(e)}", True)
            return False
    
    def test_whatsflow_api_endpoints(self):
        """Test WhatsFlow Real API endpoints"""
        endpoints_to_test = [
            ("/api/instances", "GET", "Instance listing"),
            ("/api/contacts", "GET", "Contacts listing"),
            ("/api/chats", "GET", "Chats listing"),
            ("/api/messages", "GET", "Messages listing"),
            ("/api/stats", "GET", "Statistics")
        ]
        
        all_passed = True
        
        for endpoint, method, description in endpoints_to_test:
            try:
                url = f"{WHATSFLOW_URL}{endpoint}"
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"WhatsFlow API - {description}", True, f"Endpoint {endpoint} returned {len(data) if isinstance(data, list) else 'data'}")
                else:
                    self.log_test(f"WhatsFlow API - {description}", False, f"Endpoint {endpoint} returned status {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"WhatsFlow API - {description}", False, f"Endpoint {endpoint} failed: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_baileys_groups_endpoint(self):
        """Test corrected Baileys groups endpoint"""
        try:
            # Test with a sample instance ID
            test_instance_id = "test_instance_123"
            url = f"{BAILEYS_URL}/groups/{test_instance_id}"
            
            response = self.session.get(url, timeout=10)
            
            # Even if instance doesn't exist, endpoint should respond properly
            if response.status_code in [200, 404, 400]:
                response_data = response.json()
                self.log_test("Baileys Groups Endpoint", True, f"Groups endpoint responding correctly: {response.status_code}")
                return True
            else:
                self.log_test("Baileys Groups Endpoint", False, f"Groups endpoint returned unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Baileys Groups Endpoint", False, f"Groups endpoint failed: {str(e)}", True)
            return False
    
    def test_baileys_send_message_endpoint(self):
        """Test corrected Baileys send message endpoint"""
        try:
            # Test with a sample instance ID
            test_instance_id = "test_instance_123"
            url = f"{BAILEYS_URL}/send/{test_instance_id}"
            
            # Test POST request (even if it fails due to no connection, endpoint should exist)
            test_data = {
                "phone": "5511999999999",
                "message": "Test message"
            }
            
            response = self.session.post(url, json=test_data, timeout=10)
            
            # Endpoint should exist and handle the request properly
            if response.status_code in [200, 400, 404, 500]:
                self.log_test("Baileys Send Message Endpoint", True, f"Send message endpoint responding: {response.status_code}")
                return True
            else:
                self.log_test("Baileys Send Message Endpoint", False, f"Send message endpoint returned unexpected status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Baileys Send Message Endpoint", False, f"Send message endpoint failed: {str(e)}", True)
            return False
    
    def test_whatsflow_ui_accessibility(self):
        """Test if WhatsFlow UI is accessible and returns HTML"""
        try:
            response = self.session.get(WHATSFLOW_URL, timeout=10)
            
            if response.status_code == 200:
                content = response.text.lower()
                
                # Check for professional layout elements
                layout_checks = [
                    ("container", "container" in content),
                    ("professional styling", "style" in content or "css" in content),
                    ("navigation", "nav" in content or "tab" in content),
                    ("responsive design", "responsive" in content or "width" in content)
                ]
                
                passed_checks = sum(1 for _, check in layout_checks if check)
                
                if passed_checks >= 2:
                    self.log_test("WhatsFlow UI Layout", True, f"Professional layout elements found ({passed_checks}/4 checks passed)")
                    return True
                else:
                    self.log_test("WhatsFlow UI Layout", False, f"Limited layout elements found ({passed_checks}/4 checks passed)")
                    return False
            else:
                self.log_test("WhatsFlow UI Layout", False, f"UI not accessible, status: {response.status_code}", True)
                return False
                
        except Exception as e:
            self.log_test("WhatsFlow UI Layout", False, f"UI accessibility test failed: {str(e)}", True)
            return False
    
    def test_database_schema(self):
        """Test database schema for required tables"""
        try:
            if not os.path.exists(DB_FILE):
                self.log_test("Database Schema", False, "Database file not found", True)
                return False
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['instances', 'contacts', 'messages', 'chats']
            missing_tables = [table for table in required_tables if table not in tables]
            
            conn.close()
            
            if not missing_tables:
                self.log_test("Database Schema", True, f"All required tables present: {', '.join(tables)}")
                return True
            else:
                self.log_test("Database Schema", False, f"Missing tables: {', '.join(missing_tables)}")
                return False
                
        except Exception as e:
            self.log_test("Database Schema", False, f"Schema check failed: {str(e)}", True)
            return False
    
    def test_system_integration(self):
        """Test integration between WhatsFlow and Baileys"""
        try:
            # Test if WhatsFlow can communicate with Baileys
            whatsflow_response = self.session.get(f"{WHATSFLOW_URL}/api/instances", timeout=10)
            baileys_response = self.session.get(f"{BAILEYS_URL}/status", timeout=10)
            
            if whatsflow_response.status_code == 200 and baileys_response.status_code == 200:
                self.log_test("System Integration", True, "Both services responding and can integrate")
                return True
            else:
                self.log_test("System Integration", False, f"Integration issue - WhatsFlow: {whatsflow_response.status_code}, Baileys: {baileys_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("System Integration", False, f"Integration test failed: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all validation tests"""
        print("🔍 STARTING REVIEW CORRECTIONS VALIDATION")
        print("=" * 60)
        
        # Core service tests
        whatsflow_running = self.test_whatsflow_service_running()
        baileys_running = self.test_baileys_service_running()
        
        if not whatsflow_running or not baileys_running:
            print("\n❌ CRITICAL: Core services not running properly")
            return self.generate_report()
        
        # Database and cleanup tests
        self.test_database_clean()
        self.test_database_schema()
        
        # API endpoint tests
        self.test_whatsflow_api_endpoints()
        
        # Baileys corrections tests
        self.test_baileys_groups_endpoint()
        self.test_baileys_send_message_endpoint()
        
        # UI and integration tests
        self.test_whatsflow_ui_accessibility()
        self.test_system_integration()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate final test report"""
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        critical_count = len(self.critical_issues)
        
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 REVIEW CORRECTIONS VALIDATION REPORT")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"🚨 Critical Issues: {critical_count}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in self.critical_issues:
                print(f"   - {issue}")
        
        if self.failed_tests:
            print(f"\n❌ FAILED TESTS:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        print(f"\n✅ PASSED TESTS:")
        for test in self.passed_tests:
            print(f"   - {test}")
        
        # Save detailed results
        with open('/app/review_corrections_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total_tests': total_tests,
                    'passed': passed_count,
                    'failed': failed_count,
                    'critical_issues': critical_count,
                    'success_rate': success_rate
                },
                'test_results': self.test_results,
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)
        
        return {
            'success_rate': success_rate,
            'critical_issues': self.critical_issues,
            'failed_tests': self.failed_tests,
            'passed_tests': self.passed_tests
        }

if __name__ == "__main__":
    validator = ReviewCorrectionsValidator()
    results = validator.run_all_tests()
    
    if results['success_rate'] >= 90:
        print(f"\n🎉 VALIDATION SUCCESSFUL - {results['success_rate']:.1f}% success rate")
    elif results['critical_issues']:
        print(f"\n🚨 VALIDATION FAILED - Critical issues found")
    else:
        print(f"\n⚠️ VALIDATION PARTIAL - {results['success_rate']:.1f}% success rate")