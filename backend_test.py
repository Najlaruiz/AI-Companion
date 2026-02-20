import requests
import sys
import json
from datetime import datetime

class PrivateAfterDarkAPITester:
    def __init__(self, base_url="https://private-staging.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)

            print(f"   Response Status: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED - Status: {response.status_code}")
                
                # Try to parse response
                try:
                    response_json = response.json()
                    print(f"   Response: {json.dumps(response_json, indent=2)}")
                    return success, response_json
                except:
                    print(f"   Response (text): {response.text[:200]}")
                    return success, response.text
            else:
                print(f"❌ FAILED - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test /api/ endpoint"""
        return self.run_test(
            "Root API endpoint",
            "GET",
            "/api/",
            200
        )

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        return self.run_test(
            "Health check endpoint", 
            "GET",
            "/api/health",
            200
        )

    def test_telegram_info_endpoint(self):
        """Test /api/telegram/info endpoint"""
        return self.run_test(
            "Telegram info endpoint",
            "GET", 
            "/api/telegram/info",
            200
        )

    def test_stripe_checkout_create(self):
        """Test /api/checkout/create endpoint"""
        test_data = {
            "telegram_id": "123456789",
            "tier": "premium", 
            "origin_url": "https://private-staging.preview.emergentagent.com"
        }
        return self.run_test(
            "Stripe checkout creation",
            "POST",
            "/api/checkout/create", 
            200,
            data=test_data
        )

    def test_telegram_webhook_endpoint(self):
        """Test /api/webhook/telegram endpoint"""
        test_data = {
            "update_id": 123,
            "message": {
                "message_id": 1,
                "from": {
                    "id": 123456789,
                    "username": "testuser",
                    "first_name": "Test"
                },
                "chat": {
                    "id": 123456789,
                    "type": "private"
                },
                "date": 1640995200,
                "text": "/start"
            }
        }
        return self.run_test(
            "Telegram webhook endpoint",
            "POST", 
            "/api/webhook/telegram",
            200,
            data=test_data
        )

def main():
    print("🚀 Starting Private After Dark API Tests")
    print("=" * 50)
    
    # Setup
    tester = PrivateAfterDarkAPITester()
    
    # Test basic endpoints
    print("\n📋 Testing Basic Endpoints:")
    tester.test_root_endpoint()
    tester.test_health_endpoint()
    
    # Test Telegram endpoints
    print("\n📱 Testing Telegram Integration:")
    tester.test_telegram_info_endpoint()
    tester.test_telegram_webhook_endpoint()
    
    # Test Stripe endpoints  
    print("\n💳 Testing Stripe Integration:")
    tester.test_stripe_checkout_create()

    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests PASSED!")
        return 0
    else:
        print("⚠️  Some tests FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())