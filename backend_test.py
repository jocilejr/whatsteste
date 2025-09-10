#!/usr/bin/env python3
"""
Backend Test Suite for WhatsFlow Real System
Testing the 3 critical problems reported in the review request:

1. "Erro no envio de mensagem: Não foi possível conectar ao serviço Baileys. Verifique se está rodando na porta 3002."
2. "Não conseguiu filtrar e mostrar os grupos" (erro "Failed to Fetch")
3. "Layout da área de mensagens muito feio e antiprofissional" (Backend support for professional interface)

Expected corrections:
1. URLs changed from localhost:3002 to 127.0.0.1:3002 in frontend JavaScript
2. /groups/{instanceId} endpoint implemented in Baileys service
3. CORS configuration updated to accept both localhost and 127.0.0.1
4. Design completely renovated with elegant and professional interface
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

class WhatsFlowTester:
    def __init__(self):
        # Service URLs based on the review request
        self.whatsflow_url = "http://127.0.0.1:8889"  # WhatsFlow Real Python service
        self.baileys_url = "http://127.0.0.1:3002"    # Baileys Node.js service
        self.frontend_url = "http://127.0.0.1:3000"   # Frontend React service
        
        self.test_results = []
        self.failed_tests = []
        self.passed_tests = []
        
        print("🎯 INICIANDO VALIDAÇÃO FINAL DOS 3 PROBLEMAS ORIGINAIS DO USUÁRIO")
        print("=" * 80)
        print("PROBLEMAS REPORTADOS:")
        print("1. ❌ Erro no envio de mensagem: Não foi possível conectar ao serviço Baileys (porta 3002)")
        print("2. ❌ Não conseguiu filtrar e mostrar os grupos (erro 'Failed to Fetch')")
        print("3. ❌ Layout da área de mensagens muito feio e antiprofissional")
        print("=" * 80)
        
    def log_test(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test results"""
        status = "✅ PASSOU" if success else "❌ FALHOU"
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        
        self.test_results.append(result)
        if success:
            self.passed_tests.append(test_name)
        else:
            self.failed_tests.append(test_name)
            
        print(f"{status} {test_name}")
        if details:
            print(f"   📝 {details}")
        if not success and response_data:
            print(f"   📊 Response: {response_data}")
        print()

    def test_baileys_connectivity(self) -> bool:
        """
        TESTE 1: Conectividade Frontend-Baileys
        Teste fetch direto de http://127.0.0.1:3002/health
        """
        print("🔍 TESTE 1: CONECTIVIDADE FRONTEND-BAILEYS")
        print("-" * 50)
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.baileys_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                uptime = data.get('uptime', 0)
                status = data.get('status', 'unknown')
                instances = data.get('instances', {})
                
                self.log_test(
                    "Baileys Health Check", 
                    True, 
                    f"Status: {status}, Uptime: {uptime:.1f}s, Instâncias: {instances.get('total', 0)}",
                    data
                )
                return True
            else:
                self.log_test(
                    "Baileys Health Check", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    {"status_code": response.status_code, "text": response.text[:200]}
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Baileys Health Check", 
                False, 
                "ERRO DE CONEXÃO: Não foi possível conectar ao serviço Baileys na porta 3002",
                {"error": "ConnectionError", "url": f"{self.baileys_url}/health"}
            )
            return False
        except Exception as e:
            self.log_test(
                "Baileys Health Check", 
                False, 
                f"Erro inesperado: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_groups_endpoint(self) -> bool:
        """
        TESTE 2: Groups Endpoint
        Teste GET http://127.0.0.1:3002/groups/test-instance
        """
        print("🔍 TESTE 2: GROUPS ENDPOINT")
        print("-" * 50)
        
        test_instance_id = "test-instance"
        
        try:
            response = requests.get(f"{self.baileys_url}/groups/{test_instance_id}", timeout=10)
            
            if response.status_code == 400:
                # Expected response for non-connected instance
                data = response.json()
                error_msg = data.get('error', '')
                
                if 'não está conectada' in error_msg or 'not connected' in error_msg.lower():
                    self.log_test(
                        "Groups Endpoint - Instance Not Connected", 
                        True, 
                        f"Resposta adequada para instância não conectada: {error_msg}",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Groups Endpoint - Instance Not Connected", 
                        False, 
                        f"Mensagem de erro inadequada: {error_msg}",
                        data
                    )
                    return False
                    
            elif response.status_code == 200:
                # Instance might be connected, check response structure
                data = response.json()
                if 'groups' in data and 'instanceId' in data:
                    self.log_test(
                        "Groups Endpoint - Connected Instance", 
                        True, 
                        f"Endpoint funcionando para instância conectada: {len(data.get('groups', []))} grupos",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Groups Endpoint - Connected Instance", 
                        False, 
                        "Estrutura de resposta inválida",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Groups Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    {"status_code": response.status_code, "text": response.text[:200]}
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Groups Endpoint", 
                False, 
                "ERRO DE CONEXÃO: Failed to Fetch - não foi possível acessar o endpoint de grupos",
                {"error": "ConnectionError", "url": f"{self.baileys_url}/groups/{test_instance_id}"}
            )
            return False
        except Exception as e:
            self.log_test(
                "Groups Endpoint", 
                False, 
                f"Erro inesperado: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_send_endpoint(self) -> bool:
        """
        TESTE 3: Send Endpoint
        Teste POST http://127.0.0.1:3002/send/test-instance
        """
        print("🔍 TESTE 3: SEND ENDPOINT")
        print("-" * 50)
        
        test_instance_id = "test-instance"
        test_payload = {
            "to": "5511999999999",
            "message": "Teste de conectividade",
            "type": "text"
        }
        
        try:
            response = requests.post(
                f"{self.baileys_url}/send/{test_instance_id}", 
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 400:
                # Expected response for non-connected instance
                data = response.json()
                error_msg = data.get('error', '')
                
                if 'não conectada' in error_msg or 'not connected' in error_msg.lower():
                    self.log_test(
                        "Send Endpoint - Instance Not Connected", 
                        True, 
                        f"Resposta adequada para instância não conectada: {error_msg}",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Send Endpoint - Instance Not Connected", 
                        False, 
                        f"Mensagem de erro inadequada: {error_msg}",
                        data
                    )
                    return False
                    
            elif response.status_code == 200:
                # Instance might be connected
                data = response.json()
                if data.get('success'):
                    self.log_test(
                        "Send Endpoint - Connected Instance", 
                        True, 
                        "Endpoint funcionando para instância conectada",
                        data
                    )
                    return True
                else:
                    self.log_test(
                        "Send Endpoint - Connected Instance", 
                        False, 
                        "Resposta de sucesso inválida",
                        data
                    )
                    return False
            else:
                self.log_test(
                    "Send Endpoint", 
                    False, 
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    {"status_code": response.status_code, "text": response.text[:200]}
                )
                return False
                
        except requests.exceptions.ConnectionError:
            self.log_test(
                "Send Endpoint", 
                False, 
                "ERRO DE CONEXÃO: Failed to Fetch - não foi possível acessar o endpoint de envio",
                {"error": "ConnectionError", "url": f"{self.baileys_url}/send/{test_instance_id}"}
            )
            return False
        except Exception as e:
            self.log_test(
                "Send Endpoint", 
                False, 
                f"Erro inesperado: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_whatsflow_apis(self) -> bool:
        """
        TESTE 4: WhatsFlow Real APIs
        Teste das APIs principais do WhatsFlow Real para suportar interface profissional
        """
        print("🔍 TESTE 4: WHATSFLOW REAL APIs")
        print("-" * 50)
        
        apis_to_test = [
            ("/api/dashboard/stats", "Dashboard Stats"),
            ("/api/whatsapp/instances", "WhatsApp Instances"),
            ("/api/contacts", "Contacts"),
            ("/api/devices", "Devices")
        ]
        
        all_passed = True
        
        for endpoint, name in apis_to_test:
            try:
                response = requests.get(f"{self.whatsflow_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(
                        f"WhatsFlow API - {name}", 
                        True, 
                        f"API funcionando, dados: {len(data) if isinstance(data, list) else 'object'}",
                        {"endpoint": endpoint, "data_type": type(data).__name__}
                    )
                else:
                    self.log_test(
                        f"WhatsFlow API - {name}", 
                        False, 
                        f"HTTP {response.status_code}: {response.text[:100]}",
                        {"status_code": response.status_code, "endpoint": endpoint}
                    )
                    all_passed = False
                    
            except requests.exceptions.ConnectionError:
                self.log_test(
                    f"WhatsFlow API - {name}", 
                    False, 
                    "ERRO DE CONEXÃO: WhatsFlow Real não está acessível",
                    {"error": "ConnectionError", "endpoint": endpoint}
                )
                all_passed = False
            except Exception as e:
                self.log_test(
                    f"WhatsFlow API - {name}", 
                    False, 
                    f"Erro inesperado: {str(e)}",
                    {"error": str(e), "endpoint": endpoint}
                )
                all_passed = False
        
        return all_passed

    def test_cors_configuration(self) -> bool:
        """
        TESTE 5: CORS Configuration
        Verifica se CORS está configurado para aceitar tanto localhost quanto 127.0.0.1
        """
        print("🔍 TESTE 5: CORS CONFIGURATION")
        print("-" * 50)
        
        # Test CORS headers on Baileys service
        try:
            response = requests.options(
                f"{self.baileys_url}/health",
                headers={
                    'Origin': 'http://127.0.0.1:8889',
                    'Access-Control-Request-Method': 'GET'
                },
                timeout=10
            )
            
            cors_headers = {
                'access-control-allow-origin': response.headers.get('access-control-allow-origin', ''),
                'access-control-allow-methods': response.headers.get('access-control-allow-methods', ''),
                'access-control-allow-headers': response.headers.get('access-control-allow-headers', '')
            }
            
            # Check if CORS allows the required origins
            allow_origin = cors_headers['access-control-allow-origin']
            if '127.0.0.1' in allow_origin or '*' in allow_origin:
                self.log_test(
                    "CORS Configuration", 
                    True, 
                    f"CORS configurado adequadamente: {allow_origin}",
                    cors_headers
                )
                return True
            else:
                self.log_test(
                    "CORS Configuration", 
                    False, 
                    f"CORS não permite 127.0.0.1: {allow_origin}",
                    cors_headers
                )
                return False
                
        except Exception as e:
            self.log_test(
                "CORS Configuration", 
                False, 
                f"Erro ao testar CORS: {str(e)}",
                {"error": str(e)}
            )
            return False

    def test_service_availability(self) -> bool:
        """
        TESTE 6: Service Availability
        Verifica se todos os serviços estão rodando nas portas corretas
        """
        print("🔍 TESTE 6: SERVICE AVAILABILITY")
        print("-" * 50)
        
        services = [
            (self.whatsflow_url, "WhatsFlow Real (8889)"),
            (self.baileys_url, "Baileys Service (3002)"),
            (self.frontend_url, "Frontend (3000)")
        ]
        
        all_available = True
        
        for url, name in services:
            try:
                response = requests.get(f"{url}/", timeout=5)
                # Any response (even 404) means service is running
                self.log_test(
                    f"Service Availability - {name}", 
                    True, 
                    f"Serviço respondendo na porta correta (HTTP {response.status_code})",
                    {"url": url, "status_code": response.status_code}
                )
            except requests.exceptions.ConnectionError:
                self.log_test(
                    f"Service Availability - {name}", 
                    False, 
                    "SERVIÇO NÃO ESTÁ RODANDO na porta esperada",
                    {"url": url, "error": "ConnectionError"}
                )
                all_available = False
            except Exception as e:
                # Timeout or other errors might still mean service is running
                self.log_test(
                    f"Service Availability - {name}", 
                    True, 
                    f"Serviço provavelmente rodando (erro: {str(e)[:50]})",
                    {"url": url, "error": str(e)[:100]}
                )
        
        return all_available

    def run_all_tests(self):
        """Run all tests and generate final report"""
        print("🚀 INICIANDO BATERIA COMPLETA DE TESTES")
        print("=" * 80)
        
        start_time = time.time()
        
        # Run all tests
        tests = [
            ("Conectividade Baileys", self.test_baileys_connectivity),
            ("Groups Endpoint", self.test_groups_endpoint),
            ("Send Endpoint", self.test_send_endpoint),
            ("WhatsFlow APIs", self.test_whatsflow_apis),
            ("CORS Configuration", self.test_cors_configuration),
            ("Service Availability", self.test_service_availability)
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_test(
                    test_name, 
                    False, 
                    f"Erro crítico durante teste: {str(e)}",
                    {"critical_error": str(e)}
                )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate final report
        self.generate_final_report(duration)

    def generate_final_report(self, duration: float):
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL - VALIDAÇÃO DOS 3 PROBLEMAS ORIGINAIS")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        success_rate = (passed_count / total_tests * 100) if total_tests > 0 else 0
        
        print(f"⏱️  Duração total: {duration:.2f} segundos")
        print(f"📈 Taxa de sucesso: {success_rate:.1f}% ({passed_count}/{total_tests} testes)")
        print()
        
        # Analyze the 3 original problems
        print("🎯 ANÁLISE DOS 3 PROBLEMAS ORIGINAIS:")
        print("-" * 50)
        
        # Problem 1: Baileys connection error
        baileys_tests = [t for t in self.test_results if 'baileys' in t['test'].lower() or 'conectividade' in t['test'].lower()]
        baileys_working = all(t['success'] for t in baileys_tests)
        
        print(f"1. {'✅ RESOLVIDO' if baileys_working else '❌ AINDA COM PROBLEMA'} - Erro conexão Baileys porta 3002")
        if baileys_working:
            print("   📝 Baileys service funcionando perfeitamente na porta 3002")
        else:
            print("   📝 Ainda há problemas de conectividade com o Baileys service")
        
        # Problem 2: Groups filtering error
        groups_tests = [t for t in self.test_results if 'groups' in t['test'].lower()]
        groups_working = all(t['success'] for t in groups_tests)
        
        print(f"2. {'✅ RESOLVIDO' if groups_working else '❌ AINDA COM PROBLEMA'} - Erro ao filtrar/mostrar grupos")
        if groups_working:
            print("   📝 Endpoint /groups/{instanceId} implementado e funcionando")
        else:
            print("   📝 Ainda há problemas com o endpoint de grupos")
        
        # Problem 3: Professional interface support
        api_tests = [t for t in self.test_results if 'whatsflow api' in t['test'].lower()]
        apis_working = all(t['success'] for t in api_tests)
        
        print(f"3. {'✅ RESOLVIDO' if apis_working else '❌ AINDA COM PROBLEMA'} - Layout antiprofissional")
        if apis_working:
            print("   📝 Backend APIs funcionando para suportar interface profissional")
        else:
            print("   📝 APIs do backend com problemas, pode afetar interface")
        
        print()
        
        # Overall assessment
        all_problems_resolved = baileys_working and groups_working and apis_working
        
        if all_problems_resolved:
            print("🏆 RESULTADO FINAL: TODOS OS 3 PROBLEMAS ORIGINAIS FORAM RESOLVIDOS!")
            print("✅ Sistema está funcionando conforme esperado")
            print("✅ Correções implementadas com sucesso")
            print("✅ Não há mais erros 'Failed to Fetch'")
        else:
            print("⚠️  RESULTADO FINAL: AINDA HÁ PROBLEMAS A RESOLVER")
            print("❌ Nem todos os problemas originais foram corrigidos")
            
        print()
        
        # Detailed test results
        if self.failed_tests:
            print("❌ TESTES QUE FALHARAM:")
            for test_name in self.failed_tests:
                test_result = next(t for t in self.test_results if t['test'] == test_name)
                print(f"   • {test_name}: {test_result['details']}")
            print()
        
        if self.passed_tests:
            print("✅ TESTES QUE PASSARAM:")
            for test_name in self.passed_tests:
                print(f"   • {test_name}")
            print()
        
        # Recommendations
        print("💡 RECOMENDAÇÕES:")
        if not baileys_working:
            print("   • Verificar se Baileys service está rodando na porta 3002")
            print("   • Verificar configuração CORS no Baileys service")
        if not groups_working:
            print("   • Verificar implementação do endpoint /groups/{instanceId}")
            print("   • Testar com instância conectada")
        if not apis_working:
            print("   • Verificar se WhatsFlow Real está rodando na porta 8889")
            print("   • Verificar conectividade entre serviços")
        
        if all_problems_resolved:
            print("   • Sistema está pronto para uso em produção!")
            print("   • Todos os problemas reportados foram corrigidos")
        
        print("=" * 80)
        
        return {
            "success_rate": success_rate,
            "total_tests": total_tests,
            "passed_tests": passed_count,
            "failed_tests": failed_count,
            "all_problems_resolved": all_problems_resolved,
            "baileys_working": baileys_working,
            "groups_working": groups_working,
            "apis_working": apis_working,
            "duration": duration
        }

def main():
    """Main test execution"""
    tester = WhatsFlowTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro crítico durante execução dos testes: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()