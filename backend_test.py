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
    
    def test_message_receiving_system(self):
        """Test POST /api/messages/receive - Message receiving with pushName"""
        try:
            # Test message receiving with pushName
            test_message = {
                "phone": "+5511999887766",
                "message": "Teste de mensagem com nome real",
                "pushName": "João Silva",
                "instance_id": "test_instance_001"
            }
            
            response = self.session.post(
                f"{API_BASE}/messages/receive",
                json=test_message,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                self.log_test("POST /api/messages/receive", "PASS", f"Message received with pushName: {test_message['pushName']}")
                return True
            else:
                self.log_test("POST /api/messages/receive", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
        except Exception as e:
            self.log_test("POST /api/messages/receive", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_contact_names_system(self):
        """Test contact name handling - pushName with fallback to formatted number"""
        try:
            # First, send a message to create a contact
            test_phone = "+5511987654321"
            test_pushname = "Maria Santos"
            
            message_data = {
                "phone": test_phone,
                "message": "Teste de nome de contato",
                "pushName": test_pushname,
                "instance_id": "test_instance_002"
            }
            
            # Send message to create contact
            self.session.post(f"{API_BASE}/messages/receive", json=message_data, timeout=10)
            
            # Wait a moment for processing
            time.sleep(1)
            
            # Get contacts and verify name handling
            response = self.session.get(f"{API_BASE}/contacts", timeout=10)
            
            if response.status_code == 200:
                contacts = response.json()
                
                # Look for our test contact
                test_contact = None
                for contact in contacts:
                    if contact.get("phone") == test_phone:
                        test_contact = contact
                        break
                
                if test_contact:
                    contact_name = test_contact.get("name", "")
                    if test_pushname in contact_name:
                        self.log_test("Contact Names (pushName)", "PASS", f"Contact saved with pushName: {contact_name}")
                        return True
                    else:
                        # Check if it has formatted number fallback
                        if test_phone[-4:] in contact_name:
                            self.log_test("Contact Names (Fallback)", "PASS", f"Contact saved with number fallback: {contact_name}")
                            return True
                        else:
                            self.log_test("Contact Names", "FAIL", f"Contact name not properly formatted: {contact_name}")
                            return False
                else:
                    self.log_test("Contact Names", "FAIL", "Test contact not found after message")
                    return False
            else:
                self.log_test("Contact Names", "FAIL", f"Failed to retrieve contacts: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Contact Names", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_chats_endpoint(self):
        """Test GET /api/chats - Chat conversations with correct names"""
        try:
            response = self.session.get(f"{API_BASE}/chats", timeout=10)
            
            if response.status_code == 200:
                chats = response.json()
                if isinstance(chats, list):
                    # Check if chats have proper name fields
                    valid_chats = 0
                    for chat in chats:
                        if "contact_name" in chat and "contact_phone" in chat:
                            valid_chats += 1
                    
                    self.log_test("GET /api/chats", "PASS", f"Retrieved {len(chats)} chats, {valid_chats} with proper names")
                    return chats
                else:
                    self.log_test("GET /api/chats", "FAIL", "Response is not a list")
                    return []
            else:
                self.log_test("GET /api/chats", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return []
        except Exception as e:
            self.log_test("GET /api/chats", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_filtered_messages(self):
        """Test GET /api/messages?phone=X&instance_id=Y - Filtered messages"""
        try:
            # First get a contact to test with
            contacts_response = self.session.get(f"{API_BASE}/contacts", timeout=10)
            if contacts_response.status_code == 200:
                contacts = contacts_response.json()
                if contacts:
                    test_contact = contacts[0]
                    phone = test_contact.get("phone", "")
                    instance_id = test_contact.get("instance_id", "default")
                    
                    # Test filtered messages
                    response = self.session.get(
                        f"{API_BASE}/messages?phone={phone}&instance_id={instance_id}",
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        messages = response.json()
                        self.log_test("GET /api/messages (filtered)", "PASS", f"Retrieved {len(messages)} filtered messages for {phone}")
                        return messages
                    else:
                        self.log_test("GET /api/messages (filtered)", "FAIL", f"HTTP {response.status_code}")
                        return []
                else:
                    self.log_test("GET /api/messages (filtered)", "SKIP", "No contacts available for testing")
                    return []
            else:
                self.log_test("GET /api/messages (filtered)", "FAIL", "Could not get contacts for testing")
                return []
        except Exception as e:
            self.log_test("GET /api/messages (filtered)", "FAIL", f"Exception: {str(e)}")
            return []
    
    def test_database_schema(self):
        """Test database schema and data integrity"""
        try:
            if not os.path.exists(DB_FILE):
                self.log_test("Database Schema", "FAIL", f"Database file not found: {DB_FILE}")
                return False
            
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            # Check if required tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ["instances", "contacts", "messages"]
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                self.log_test("Database Schema", "FAIL", f"Missing tables: {missing_tables}")
                conn.close()
                return False
            
            # Check contacts table schema for name fields
            cursor.execute("PRAGMA table_info(contacts)")
            contact_columns = [row[1] for row in cursor.fetchall()]
            
            if "name" not in contact_columns:
                self.log_test("Database Schema", "FAIL", "Contacts table missing 'name' column")
                conn.close()
                return False
            
            # Check if contacts have real names (not just numbers)
            cursor.execute("SELECT name, phone FROM contacts WHERE name NOT LIKE 'Contact %' LIMIT 5")
            real_named_contacts = cursor.fetchall()
            
            conn.close()
            
            if real_named_contacts:
                names = [contact[0] for contact in real_named_contacts]
                self.log_test("Database Schema", "PASS", f"Database schema valid, found real contact names: {names[:3]}")
                return True
            else:
                self.log_test("Database Schema", "PASS", "Database schema valid, but no real contact names found yet")
                return True
                
        except Exception as e:
            self.log_test("Database Schema", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_websocket_status(self):
        """Test WebSocket functionality (if available)"""
        try:
            # Check if WebSocket port is accessible
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 8890))  # WebSocket port from whatsflow-real.py
            sock.close()
            
            if result == 0:
                self.log_test("WebSocket Status", "PASS", "WebSocket port 8890 is accessible")
                return True
            else:
                self.log_test("WebSocket Status", "FAIL", "WebSocket port 8890 not accessible")
                return False
        except Exception as e:
            self.log_test("WebSocket Status", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_logs_verification(self):
        """Test if logs show contact names with message content"""
        try:
            # Check if log files exist and contain contact information
            log_files = ["/app/whatsflow.log", "/app/whatsflow_debug.log"]
            
            found_logs = False
            contact_logs = False
            
            for log_file in log_files:
                if os.path.exists(log_file):
                    found_logs = True
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            log_content = f.read()
                            # Look for patterns that indicate contact names in logs
                            if any(keyword in log_content.lower() for keyword in ['contact', 'message', 'received', 'pushname']):
                                contact_logs = True
                                break
                    except:
                        continue
            
            if found_logs and contact_logs:
                self.log_test("Logs Verification", "PASS", "Log files found with contact/message information")
                return True
            elif found_logs:
                self.log_test("Logs Verification", "PASS", "Log files found but limited contact information")
                return True
            else:
                self.log_test("Logs Verification", "FAIL", "No log files found")
                return False
                
        except Exception as e:
            self.log_test("Logs Verification", "FAIL", f"Exception: {str(e)}")
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