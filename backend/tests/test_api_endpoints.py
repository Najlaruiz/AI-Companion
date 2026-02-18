"""
Backend API Tests for Private After Dark - Iteration 4
Tests: /api/health, /api/telegram/info endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://paywall-staging.preview.emergentagent.com')

class TestHealthEndpoint:
    """Health endpoint tests"""
    
    def test_health_returns_200(self):
        """Test /api/health returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        print(f"Health endpoint returned: {response.json()}")
    
    def test_health_returns_healthy_status(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        print(f"Health status: {data['status']}")
    
    def test_health_shows_telegram_configured(self):
        """Test /api/health shows telegram_configured flag"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert "telegram_configured" in data
        assert data["telegram_configured"] == True
        print(f"Telegram configured: {data['telegram_configured']}")


class TestTelegramInfoEndpoint:
    """Telegram info endpoint tests"""
    
    def test_telegram_info_returns_200(self):
        """Test /api/telegram/info returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        assert response.status_code == 200
        print(f"Telegram info returned: {response.json()}")
    
    def test_telegram_info_shows_configured(self):
        """Test /api/telegram/info shows configured flag"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        data = response.json()
        assert "configured" in data
        assert data["configured"] == True
        print(f"Telegram configured: {data['configured']}")
    
    def test_telegram_info_returns_username(self):
        """Test /api/telegram/info returns bot username"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        data = response.json()
        assert "username" in data
        assert data["username"] == "MidnightDesireAi_bot"
        print(f"Bot username: {data['username']}")
    
    def test_telegram_info_returns_link(self):
        """Test /api/telegram/info returns bot link"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        data = response.json()
        assert "link" in data
        assert data["link"] == "https://t.me/MidnightDesireAi_bot"
        print(f"Bot link: {data['link']}")


class TestRootEndpoint:
    """Root API endpoint tests"""
    
    def test_root_returns_200(self):
        """Test /api/ returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        print(f"Root endpoint returned: {response.json()}")
    
    def test_root_returns_version(self):
        """Test /api/ returns correct version"""
        response = requests.get(f"{BASE_URL}/api/")
        data = response.json()
        assert "version" in data
        assert data["version"] == "3.0.0"
        print(f"API version: {data['version']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
