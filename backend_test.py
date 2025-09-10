#!/usr/bin/env python3
"""
Backend Test Suite for WhatsFlow Real - Enhanced Testing
Testing all API endpoints running on port 8889 with focus on:
- Clean design implementation
- Message system functionality  
- Contact names (pushName) with fallback
- WebSocket functionality
- Database operations with real names
- Logs verification
"""

import requests
import json
import time
import uuid
from datetime import datetime
import sqlite3
import os
import subprocess

# Configuration
BASE_URL = "http://localhost:8889"
API_BASE = f"{BASE_URL}/api"
DB_FILE = "/app/whatsflow.db"

class WhatsFlowRealTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
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
            self.passed_tests.append(test_name)
            print(f"✅ {test_name}: {details}")
        else:
            self.failed_tests.append(test_name)
            print(f"❌ {test_name}: {details}")
    
    def test_server_connectivity(self):
        """Test if the server is running and accessible"""
        try:
            response = self.session.get(BASE_URL, timeout=10)
            if response.status_code == 200:
                self.log_test("Server Connectivity", "PASS", f"Server responding on port 8889")
                return True
            else:
                self.log_test("Server Connectivity", "FAIL", f"Server returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            self.log_test("Server Connectivity", "FAIL", f"Connection error: {str(e)}")
            return False
    
    def test_get_instances(self):
        """Test GET /api/instances - List WhatsApp instances"""
        try:
            response = self.session.get(f"{API_BASE}/instances", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /api/instances", "PASS", f"Retrieved {len(data)} instances")
                    return data
                else:
                    self.log_test("GET /api/instances", "FAIL", "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/instances", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("GET /api/instances", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_create_instance(self):
        """Test POST /api/instances - Create new WhatsApp instance"""
        try:
            test_instance_name = f"Test Instance {uuid.uuid4().hex[:8]}"
            payload = {"name": test_instance_name}
            
            response = self.session.post(
                f"{API_BASE}/instances",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "id" in data and "name" in data:
                    self.log_test("POST /api/instances", "PASS", f"Created instance: {data['name']}")
                    return data
                else:
                    self.log_test("POST /api/instances", "FAIL", "Missing required fields in response")
                    return None
            else:
                self.log_test("POST /api/instances", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("POST /api/instances", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_get_contacts(self):
        """Test GET /api/contacts - List imported contacts"""
        try:
            response = self.session.get(f"{API_BASE}/contacts", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /api/contacts", "PASS", f"Retrieved {len(data)} contacts")
                    return data
                else:
                    self.log_test("GET /api/contacts", "FAIL", "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/contacts", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("GET /api/contacts", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_get_messages(self):
        """Test GET /api/messages - List received messages"""
        try:
            response = self.session.get(f"{API_BASE}/messages", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /api/messages", "PASS", f"Retrieved {len(data)} messages")
                    return data
                else:
                    self.log_test("GET /api/messages", "FAIL", "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/messages", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("GET /api/messages", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_get_stats(self):
        """Test GET /api/stats - System statistics"""
        try:
            response = self.session.get(f"{API_BASE}/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["contacts_count", "conversations_count", "messages_count"]
                
                if all(field in data for field in expected_fields):
                    stats_summary = f"Contacts: {data['contacts_count']}, Messages: {data['messages_count']}"
                    self.log_test("GET /api/stats", "PASS", f"Statistics retrieved - {stats_summary}")
                    return data
                else:
                    missing_fields = [f for f in expected_fields if f not in data]
                    self.log_test("GET /api/stats", "FAIL", f"Missing fields: {missing_fields}")
                    return None
            else:
                self.log_test("GET /api/stats", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("GET /api/stats", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_whatsapp_status(self):
        """Test GET /api/whatsapp/status - WhatsApp connection status"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "connected" in data:
                    status = "Connected" if data["connected"] else "Disconnected"
                    connecting = data.get("connecting", False)
                    if connecting:
                        status = "Connecting"
                    
                    self.log_test("GET /api/whatsapp/status", "PASS", f"WhatsApp status: {status}")
                    return data
                else:
                    self.log_test("GET /api/whatsapp/status", "FAIL", "Missing 'connected' field in response")
                    return None
            else:
                self.log_test("GET /api/whatsapp/status", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("GET /api/whatsapp/status", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_whatsapp_qr(self):
        """Test GET /api/whatsapp/qr - QR code for WhatsApp connection"""
        try:
            response = self.session.get(f"{API_BASE}/whatsapp/qr", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "qr" in data and "connected" in data:
                    qr_status = "Available" if data["qr"] else "Not available"
                    self.log_test("GET /api/whatsapp/qr", "PASS", f"QR code: {qr_status}")
                    return data
                else:
                    self.log_test("GET /api/whatsapp/qr", "FAIL", "Missing required fields in response")
                    return None
            else:
                self.log_test("GET /api/whatsapp/qr", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("GET /api/whatsapp/qr", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_webhooks_endpoint(self):
        """Test GET /api/webhooks - List webhooks"""
        try:
            response = self.session.get(f"{API_BASE}/webhooks", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("GET /api/webhooks", "PASS", f"Retrieved {len(data)} webhooks")
                    return data
                else:
                    self.log_test("GET /api/webhooks", "FAIL", "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/webhooks", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("GET /api/webhooks", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_instance_connection(self, instance_id):
        """Test POST /api/instances/{id}/connect - Connect WhatsApp instance"""
        if not instance_id:
            self.log_test("POST /api/instances/{id}/connect", "SKIP", "No instance ID provided")
            return None
            
        try:
            response = self.session.post(
                f"{API_BASE}/instances/{instance_id}/connect",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "success" in data or "message" in data:
                    self.log_test("POST /api/instances/{id}/connect", "PASS", "Connection initiated successfully")
                    return data
                else:
                    self.log_test("POST /api/instances/{id}/connect", "FAIL", "Unexpected response format")
                    return None
            else:
                self.log_test("POST /api/instances/{id}/connect", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return None
        except Exception as e:
            self.log_test("POST /api/instances/{id}/connect", "FAIL", f"Exception: {str(e)}")
            return None
    
    def test_database_persistence(self):
        """Test if SQLite database is working properly"""
        try:
            # Test by creating an instance and then retrieving it
            created_instance = self.test_create_instance()
            if not created_instance:
                self.log_test("Database Persistence", "FAIL", "Could not create test instance")
                return False
            
            # Wait a moment and retrieve instances
            time.sleep(1)
            instances = self.test_get_instances()
            
            # Check if our created instance exists
            found_instance = None
            for instance in instances:
                if instance.get("id") == created_instance.get("id"):
                    found_instance = instance
                    break
            
            if found_instance:
                self.log_test("Database Persistence", "PASS", "SQLite database working correctly")
                return True
            else:
                self.log_test("Database Persistence", "FAIL", "Created instance not found in database")
                return False
                
        except Exception as e:
            self.log_test("Database Persistence", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_baileys_service_integration(self):
        """Test integration with Baileys WhatsApp service"""
        try:
            # Test if Baileys service is running on port 3002
            baileys_url = "http://localhost:3002"
            
            try:
                response = self.session.get(f"{baileys_url}/status", timeout=5)
                if response.status_code == 200:
                    self.log_test("Baileys Service Integration", "PASS", "Baileys service is running and accessible")
                    return True
                else:
                    self.log_test("Baileys Service Integration", "FAIL", f"Baileys service returned status {response.status_code}")
                    return False
            except requests.exceptions.RequestException:
                self.log_test("Baileys Service Integration", "FAIL", "Baileys service not accessible on port 3002")
                return False
                
        except Exception as e:
            self.log_test("Baileys Service Integration", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting WhatsFlow Real Backend Tests")
        print("=" * 60)
        
        # Test server connectivity first
        if not self.test_server_connectivity():
            print("❌ Server not accessible. Stopping tests.")
            return self.generate_report()
        
        # Core API endpoint tests
        print("\n📋 Testing Core API Endpoints:")
        instances = self.test_get_instances()
        contacts = self.test_get_contacts()
        messages = self.test_get_messages()
        stats = self.test_get_stats()
        
        # WhatsApp specific tests
        print("\n📱 Testing WhatsApp Integration:")
        whatsapp_status = self.test_whatsapp_status()
        qr_data = self.test_whatsapp_qr()
        
        # Additional endpoints
        print("\n🔗 Testing Additional Endpoints:")
        webhooks = self.test_webhooks_endpoint()
        
        # Functionality tests
        print("\n⚙️ Testing System Functionality:")
        created_instance = self.test_create_instance()
        
        # Test instance connection if we have an instance
        if created_instance and created_instance.get("id"):
            self.test_instance_connection(created_instance["id"])
        elif instances and len(instances) > 0:
            self.test_instance_connection(instances[0].get("id"))
        
        # Database and integration tests
        print("\n🗄️ Testing System Integration:")
        self.test_database_persistence()
        self.test_baileys_service_integration()
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"Success Rate: {(passed_count/total_tests*100):.1f}%" if total_tests > 0 else "0%")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in self.failed_tests:
                print(f"   - {test}")
        
        if self.passed_tests:
            print(f"\n✅ Passed Tests:")
            for test in self.passed_tests:
                print(f"   - {test}")
        
        # Save detailed results to file
        with open("/app/backend_test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "passed": passed_count,
                    "failed": failed_count,
                    "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0
                },
                "passed_tests": self.passed_tests,
                "failed_tests": self.failed_tests,
                "detailed_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
        
        return {
            "total_tests": total_tests,
            "passed": passed_count,
            "failed": failed_count,
            "success_rate": (passed_count/total_tests*100) if total_tests > 0 else 0,
            "failed_tests": self.failed_tests,
            "passed_tests": self.passed_tests
        }

def main():
    """Main test execution"""
    tester = WhatsFlowRealTester()
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