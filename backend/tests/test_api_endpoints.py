"""
Backend API Tests for Private After Dark
Tests: Health, Telegram, Checkout, Voice, Reactivation endpoints
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://private-staging.preview.emergentagent.com')

class TestHealthEndpoints:
    """Health check endpoint tests"""
    
    def test_health_returns_200(self):
        """Test /api/health returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✅ Health check passed: {data}")
    
    def test_health_shows_telegram_configured(self):
        """Test /api/health shows telegram_configured field"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "telegram_configured" in data
        assert data["telegram_configured"] == True
        print(f"✅ Telegram configured: {data['telegram_configured']}")


class TestTelegramEndpoints:
    """Telegram bot info endpoint tests"""
    
    def test_telegram_info_returns_200(self):
        """Test /api/telegram/info returns 200"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        assert response.status_code == 200
        print(f"✅ Telegram info returned: {response.json()}")
    
    def test_telegram_info_shows_bot_username(self):
        """Test /api/telegram/info returns correct bot username"""
        response = requests.get(f"{BASE_URL}/api/telegram/info")
        data = response.json()
        assert data["configured"] == True
        assert "username" in data
        assert data["username"] == "MidnightDesireAi_bot"
        assert "link" in data
        assert "t.me" in data["link"]
        print(f"✅ Bot: @{data['username']} - {data['link']}")


class TestCheckoutEndpoints:
    """Checkout and payment endpoint tests"""
    
    def test_checkout_redirect_returns_307(self):
        """Test /api/checkout/redirect creates Stripe session and redirects"""
        response = requests.get(
            f"{BASE_URL}/api/checkout/redirect",
            params={"telegram_id": "test_user_123", "tier": "premium"},
            allow_redirects=False
        )
        # Should be 307 Temporary Redirect to Stripe
        assert response.status_code == 307
        assert "location" in response.headers
        location = response.headers["location"]
        assert "checkout.stripe.com" in location
        print(f"✅ Checkout redirect works - Location: {location[:80]}...")
    
    def test_checkout_redirect_vip_tier(self):
        """Test /api/checkout/redirect works for VIP tier"""
        response = requests.get(
            f"{BASE_URL}/api/checkout/redirect",
            params={"telegram_id": "test_user_456", "tier": "vip"},
            allow_redirects=False
        )
        assert response.status_code == 307
        assert "checkout.stripe.com" in response.headers.get("location", "")
        print(f"✅ VIP checkout redirect works")
    
    def test_checkout_status_endpoint_exists(self):
        """Test /api/checkout/status/{session_id} exists"""
        response = requests.get(f"{BASE_URL}/api/checkout/status/cs_test_fake_session")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "payment_status" in data
        print(f"✅ Checkout status endpoint works: {data}")


class TestVoiceEndpoints:
    """Voice feature endpoint tests (Edge TTS)"""
    
    def test_voice_status_returns_200(self):
        """Test /api/voice/status returns 200"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        assert response.status_code == 200
        print(f"✅ Voice status: {response.json()}")
    
    def test_voice_status_enabled(self):
        """Test voice is enabled (Edge TTS is always available)"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert data.get("enabled") == True
        print(f"✅ Voice enabled: {data.get('enabled')}")
    
    def test_voice_status_provider(self):
        """Test voice provider is Edge TTS"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "provider" in data
        assert "Edge TTS" in data["provider"]
        print(f"✅ Voice provider: {data.get('provider')}")
    
    def test_voice_status_characters(self):
        """Test voice status returns all 3 characters"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "characters" in data
        characters = data["characters"]
        assert "valeria" in characters
        assert "luna" in characters
        assert "nyx" in characters
        print(f"✅ Voice characters: {characters}")
    
    def test_voice_status_styles(self):
        """Test voice status returns all 3 styles"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "styles" in data
        styles = data["styles"]
        assert "natural" in styles
        assert "dominant" in styles
        assert "whisper" in styles
        print(f"✅ Voice styles: {styles}")
    
    def test_voice_status_languages(self):
        """Test voice status returns all 4 languages"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "languages" in data
        languages = data["languages"]
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "ar" in languages
        print(f"✅ Voice languages: {languages}")


class TestReactivationEndpoints:
    """Reactivation system endpoint tests"""
    
    def test_reactivation_stats_returns_200(self):
        """Test /api/reactivation/stats returns 200"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_users" in data
        assert "hit_paywall" in data
        assert "inactive_24h" in data
        assert "reactivated_count" in data
        print(f"✅ Reactivation stats: {data}")
    
    def test_reactivation_run_post(self):
        """Test POST /api/reactivation/run queues the job"""
        response = requests.post(f"{BASE_URL}/api/reactivation/run")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        print(f"✅ Reactivation job queued: {data}")
    
    def test_reactivation_run_get_not_allowed(self):
        """Test GET /api/reactivation/run returns 405"""
        response = requests.get(f"{BASE_URL}/api/reactivation/run")
        assert response.status_code == 405
        print(f"✅ GET /reactivation/run correctly returns 405")


class TestUserVoicePreference:
    """User voice preference endpoint tests"""
    
    def test_voice_preference_natural(self):
        """Test setting voice preference to natural"""
        response = requests.post(
            f"{BASE_URL}/api/user/test_user_001/voice-preference",
            params={"preference": "natural"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["voice_preference"] == "natural"
        print(f"✅ Voice preference set: natural")
    
    def test_voice_preference_dominant(self):
        """Test setting voice preference to dominant"""
        response = requests.post(
            f"{BASE_URL}/api/user/test_user_002/voice-preference",
            params={"preference": "dominant"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["voice_preference"] == "dominant"
        print(f"✅ Voice preference set: dominant")
    
    def test_voice_preference_whisper(self):
        """Test setting voice preference to whisper"""
        response = requests.post(
            f"{BASE_URL}/api/user/test_user_003/voice-preference",
            params={"preference": "whisper"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["voice_preference"] == "whisper"
        print(f"✅ Voice preference set: whisper")
    
    def test_voice_preference_invalid_returns_400(self):
        """Test invalid voice preference returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/user/test_user_004/voice-preference",
            params={"preference": "invalid_style"}
        )
        assert response.status_code == 400
        print(f"✅ Invalid preference correctly returns 400")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
