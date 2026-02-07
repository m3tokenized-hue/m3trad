#!/usr/bin/env python3
"""
E1 Assistant Backend API Testing Suite
Tests all backend endpoints for the AI Assistant application
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

class E1AssistantTester:
    def __init__(self, base_url="https://pdf-analyzer-77.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details:
            print(f"    {details}")
        if not success and response_data:
            print(f"    Response: {response_data}")
        print()

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                    expected_status: int = 200) -> tuple[bool, Any]:
        """Make HTTP request and return success status and response data"""
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return False, f"Unsupported method: {method}"
            
            success = response.status_code == expected_status
            try:
                response_data = response.json()
            except:
                response_data = response.text
                
            return success, response_data
            
        except requests.exceptions.Timeout:
            return False, "Request timeout (30s)"
        except requests.exceptions.ConnectionError:
            return False, "Connection error - backend may be down"
        except Exception as e:
            return False, f"Request error: {str(e)}"

    def test_root_endpoint(self):
        """Test API root endpoint"""
        success, data = self.make_request('GET', '/')
        if success and isinstance(data, dict) and 'message' in data:
            self.log_test("API Root Endpoint", True, f"API version: {data.get('version', 'unknown')}")
        else:
            self.log_test("API Root Endpoint", False, "Invalid response format", data)

    def test_models_endpoint(self):
        """Test GET /api/models endpoint"""
        success, data = self.make_request('GET', '/models')
        
        if success:
            if isinstance(data, dict) and 'models' in data:
                models = data['models']
                if isinstance(models, list) and len(models) > 0:
                    # Check if required models are present
                    model_names = [m.get('name', '') for m in models]
                    has_claude = any('Claude' in name for name in model_names)
                    has_gemini = any('Gemini' in name for name in model_names)
                    has_gpt = any('GPT' in name for name in model_names)
                    
                    self.log_test("Models Endpoint", True, 
                                f"Found {len(models)} models (Claude: {has_claude}, Gemini: {has_gemini}, GPT: {has_gpt})")
                    return models
                else:
                    self.log_test("Models Endpoint", False, "No models found in response", data)
            else:
                self.log_test("Models Endpoint", False, "Invalid response format", data)
        else:
            self.log_test("Models Endpoint", False, "Request failed", data)
        return []

    def test_chat_endpoint(self):
        """Test POST /api/chat endpoint"""
        chat_data = {
            "message": "Hello, this is a test message. Please respond briefly.",
            "model": "claude-sonnet-4-5-20250929",
            "provider": "anthropic"
        }
        
        print("🔄 Sending chat message (this may take 10-15 seconds)...")
        success, data = self.make_request('POST', '/chat', chat_data)
        
        if success:
            if isinstance(data, dict) and 'message' in data and 'conversation_id' in data:
                message = data['message']
                if isinstance(message, dict) and message.get('role') == 'assistant':
                    self.log_test("Chat Endpoint", True, 
                                f"Got AI response: '{message.get('content', '')[:50]}...'")
                    return data['conversation_id']
                else:
                    self.log_test("Chat Endpoint", False, "Invalid message format", data)
            else:
                self.log_test("Chat Endpoint", False, "Invalid response format", data)
        else:
            self.log_test("Chat Endpoint", False, "Chat request failed", data)
        return None

    def test_conversations_endpoint(self, conversation_id: Optional[str] = None):
        """Test GET /api/conversations endpoint"""
        success, data = self.make_request('GET', '/conversations')
        
        if success:
            if isinstance(data, list):
                self.log_test("Conversations List", True, f"Found {len(data)} conversations")
                
                # If we have a conversation ID from chat test, try to fetch it
                if conversation_id:
                    success2, conv_data = self.make_request('GET', f'/conversations/{conversation_id}')
                    if success2 and isinstance(conv_data, dict):
                        self.log_test("Single Conversation", True, 
                                    f"Retrieved conversation: {conv_data.get('title', 'Untitled')}")
                    else:
                        self.log_test("Single Conversation", False, "Failed to retrieve conversation", conv_data)
            else:
                self.log_test("Conversations List", False, "Invalid response format", data)
        else:
            self.log_test("Conversations List", False, "Request failed", data)

    def test_webhooks_endpoint(self):
        """Test webhook endpoints"""
        # Test GET webhooks
        success, data = self.make_request('GET', '/webhooks')
        
        if success:
            if isinstance(data, list):
                self.log_test("Webhooks List", True, f"Found {len(data)} webhooks")
                
                # Test POST webhook (create)
                webhook_data = {
                    "name": "Test Webhook",
                    "description": "Test webhook for API testing",
                    "url": "https://httpbin.org/post",
                    "method": "POST",
                    "headers": {"Content-Type": "application/json"}
                }
                
                success2, create_data = self.make_request('POST', '/webhooks', webhook_data, 200)
                if success2 and isinstance(create_data, dict) and 'id' in create_data:
                    webhook_id = create_data['id']
                    self.log_test("Create Webhook", True, f"Created webhook with ID: {webhook_id}")
                    
                    # Test webhook test endpoint
                    success3, test_data = self.make_request('POST', f'/webhooks/{webhook_id}/test')
                    if success3:
                        self.log_test("Test Webhook", True, f"Webhook test result: {test_data.get('status', 'unknown')}")
                    else:
                        self.log_test("Test Webhook", False, "Webhook test failed", test_data)
                    
                    # Clean up - delete the test webhook
                    success4, _ = self.make_request('DELETE', f'/webhooks/{webhook_id}')
                    if success4:
                        self.log_test("Delete Webhook", True, "Test webhook cleaned up")
                    else:
                        self.log_test("Delete Webhook", False, "Failed to clean up test webhook")
                else:
                    self.log_test("Create Webhook", False, "Failed to create webhook", create_data)
            else:
                self.log_test("Webhooks List", False, "Invalid response format", data)
        else:
            self.log_test("Webhooks List", False, "Request failed", data)

    def test_swarm_agents_endpoint(self):
        """Test swarm agents endpoints"""
        # Test GET agents
        success, data = self.make_request('GET', '/swarm/agents')
        
        if success:
            if isinstance(data, list):
                self.log_test("Swarm Agents List", True, f"Found {len(data)} agents")
                
                # Test POST agent (create)
                agent_data = {
                    "name": "Test Analyst",
                    "role": "analyst",
                    "model": "gemini-3-flash-preview",
                    "provider": "gemini",
                    "system_prompt": "You are a test crypto market analyst for API testing."
                }
                
                success2, create_data = self.make_request('POST', '/swarm/agents', agent_data, 200)
                if success2 and isinstance(create_data, dict) and 'id' in create_data:
                    agent_id = create_data['id']
                    self.log_test("Create Swarm Agent", True, f"Created agent with ID: {agent_id}")
                    
                    # Clean up - delete the test agent
                    success3, _ = self.make_request('DELETE', f'/swarm/agents/{agent_id}')
                    if success3:
                        self.log_test("Delete Swarm Agent", True, "Test agent cleaned up")
                    else:
                        self.log_test("Delete Swarm Agent", False, "Failed to clean up test agent")
                else:
                    self.log_test("Create Swarm Agent", False, "Failed to create agent", create_data)
            else:
                self.log_test("Swarm Agents List", False, "Invalid response format", data)
        else:
            self.log_test("Swarm Agents List", False, "Request failed", data)

    def test_swarm_tasks_endpoint(self):
        """Test swarm tasks endpoints"""
        # Test GET tasks
        success, data = self.make_request('GET', '/swarm/tasks')
        
        if success:
            if isinstance(data, list):
                self.log_test("Swarm Tasks List", True, f"Found {len(data)} tasks")
            else:
                self.log_test("Swarm Tasks List", False, "Invalid response format", data)
        else:
            self.log_test("Swarm Tasks List", False, "Request failed", data)

    def test_settings_endpoint(self):
        """Test settings endpoints"""
        # Test GET settings
        success, data = self.make_request('GET', '/settings')
        
        if success:
            if isinstance(data, dict):
                self.log_test("Settings Get", True, f"Retrieved settings with default model: {data.get('default_model', 'unknown')}")
                
                # Test PUT settings (update)
                update_data = {
                    "default_model": "claude-sonnet-4-5-20250929",
                    "system_prompt": "Test system prompt for API testing"
                }
                
                success2, update_result = self.make_request('PUT', '/settings', update_data)
                if success2:
                    self.log_test("Settings Update", True, "Settings updated successfully")
                else:
                    self.log_test("Settings Update", False, "Failed to update settings", update_result)
            else:
                self.log_test("Settings Get", False, "Invalid response format", data)
        else:
            self.log_test("Settings Get", False, "Request failed", data)

    def test_crypto_prices_endpoint(self):
        """Test GET /api/crypto/prices endpoint"""
        print("🔄 Fetching crypto prices (this may take a few seconds)...")
        success, data = self.make_request('GET', '/crypto/prices')
        
        if success:
            if isinstance(data, dict) and 'prices' in data:
                prices = data['prices']
                if isinstance(prices, list) and len(prices) > 0:
                    # Check if we have expected crypto data
                    first_coin = prices[0]
                    required_fields = ['symbol', 'name', 'price', 'change_24h']
                    has_required_fields = all(field in first_coin for field in required_fields)
                    
                    if has_required_fields:
                        self.log_test("Crypto Prices Endpoint", True, 
                                    f"Found {len(prices)} cryptocurrencies. First: {first_coin.get('symbol')} at ${first_coin.get('price')}")
                    else:
                        self.log_test("Crypto Prices Endpoint", False, 
                                    f"Missing required fields in crypto data. Got: {list(first_coin.keys())}")
                else:
                    self.log_test("Crypto Prices Endpoint", False, "No crypto prices found in response", data)
            else:
                self.log_test("Crypto Prices Endpoint", False, "Invalid response format - missing 'prices' field", data)
        else:
            self.log_test("Crypto Prices Endpoint", False, "Request failed", data)

    def test_wallet_settings_endpoint(self):
        """Test wallet settings endpoints"""
        # Test GET wallet settings
        success, data = self.make_request('GET', '/wallet-settings')
        
        if success:
            if isinstance(data, dict):
                expected_fields = ['binance_connected', 'coinbase_connected']
                has_expected_fields = all(field in data for field in expected_fields)
                
                if has_expected_fields:
                    binance_status = "connected" if data.get('binance_connected') else "not connected"
                    coinbase_status = "connected" if data.get('coinbase_connected') else "not connected"
                    
                    self.log_test("Wallet Settings Get", True, 
                                f"Binance: {binance_status}, Coinbase: {coinbase_status}")
                    
                    # Test PUT wallet settings (update) - only if not already connected
                    if not data.get('binance_connected'):
                        test_wallet_data = {
                            "binance_api_key": "test_api_key_12345",
                            "binance_api_secret": "test_secret_67890"
                        }
                        
                        success2, update_result = self.make_request('PUT', '/wallet-settings', test_wallet_data)
                        if success2:
                            self.log_test("Wallet Settings Update", True, "Test wallet settings updated successfully")
                            
                            # Clean up - disconnect the test wallet
                            success3, _ = self.make_request('DELETE', '/wallet-settings/binance')
                            if success3:
                                self.log_test("Wallet Disconnect", True, "Test wallet disconnected successfully")
                            else:
                                self.log_test("Wallet Disconnect", False, "Failed to disconnect test wallet")
                        else:
                            self.log_test("Wallet Settings Update", False, "Failed to update wallet settings", update_result)
                    else:
                        self.log_test("Wallet Settings Update", True, "Skipped - Binance already connected")
                else:
                    self.log_test("Wallet Settings Get", False, 
                                f"Missing expected fields. Got: {list(data.keys())}", data)
            else:
                self.log_test("Wallet Settings Get", False, "Invalid response format", data)
        else:
            self.log_test("Wallet Settings Get", False, "Request failed", data)

    def test_kimi_model_availability(self):
        """Test if Kimi K2.5 model is available in models list"""
        success, data = self.make_request('GET', '/models')
        
        if success and isinstance(data, dict) and 'models' in data:
            models = data['models']
            kimi_models = [m for m in models if 'kimi' in m.get('model', '').lower() or 'kimi' in m.get('name', '').lower()]
            
            if kimi_models:
                kimi_model = kimi_models[0]
                self.log_test("Kimi K2.5 Model Availability", True, 
                            f"Found Kimi model: {kimi_model.get('name')} ({kimi_model.get('model')})")
            else:
                self.log_test("Kimi K2.5 Model Availability", False, 
                            "Kimi K2.5 model not found in models list")
        else:
            self.log_test("Kimi K2.5 Model Availability", False, "Could not fetch models list")

    def run_all_tests(self):
        """Run all backend API tests"""
        print("🚀 Starting E1 Assistant Backend API Tests")
        print(f"🔗 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Test basic connectivity
        self.test_root_endpoint()
        
        # Test core endpoints
        models = self.test_models_endpoint()
        self.test_kimi_model_availability()  # Test Kimi K2.5 model specifically
        conversation_id = self.test_chat_endpoint()
        self.test_conversations_endpoint(conversation_id)
        
        # Test integration endpoints
        self.test_webhooks_endpoint()
        self.test_swarm_agents_endpoint()
        self.test_swarm_tasks_endpoint()
        self.test_settings_endpoint()
        
        # Test new crypto and wallet features
        self.test_crypto_prices_endpoint()
        self.test_wallet_settings_endpoint()
        
        # Print summary
        print("=" * 60)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✨ Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend is working correctly.")
            return 0
        else:
            failed_tests = [r for r in self.test_results if not r['success']]
            print(f"⚠️  {len(failed_tests)} tests failed:")
            for test in failed_tests:
                print(f"   - {test['test_name']}: {test['details']}")
            return 1

def main():
    """Main test execution"""
    tester = E1AssistantTester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())