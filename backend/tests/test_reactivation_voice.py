"""
Backend API Tests for P1 Reactivation System with Edge TTS
Tests: /api/voice/status, /api/reactivation/stats, /api/reactivation/run, /api/health
Features: Character-specific emotional scripts, Voice teasers/messages, Timing (24h, 72h, 7d)
Voice: Edge TTS (free, always available) - natural/dominant/whisper styles
Multi-language: EN/ES/FR/AR
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://paywall-staging.preview.emergentagent.com').rstrip('/')


class TestVoiceStatusEndpoint:
    """Voice status endpoint tests - /api/voice/status - Edge TTS (FREE)"""
    
    def test_voice_status_returns_200(self):
        """Test /api/voice/status returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Voice status endpoint returned: {response.json()}")
    
    def test_voice_status_enabled_true(self):
        """Test /api/voice/status returns enabled=true (Edge TTS is always available)"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "enabled" in data, "Response should have 'enabled' field"
        # Edge TTS is free and always available - enabled should be True
        assert data["enabled"] == True, "Voice should be enabled with Edge TTS (free provider)"
        print(f"Voice enabled: {data['enabled']}")
    
    def test_voice_status_provider_edge_tts(self):
        """Test /api/voice/status returns Edge TTS provider"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "provider" in data, "Response should have 'provider' field"
        assert "Edge TTS" in data["provider"], f"Expected Edge TTS provider, got '{data.get('provider')}'"
        print(f"Voice provider: {data['provider']}")
    
    def test_voice_status_has_characters(self):
        """Test /api/voice/status returns characters list"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "characters" in data, "Response should have 'characters' field"
        assert isinstance(data["characters"], list), "Characters should be a list"
        # Should have valeria, luna, nyx
        expected_chars = ["valeria", "luna", "nyx"]
        for char in expected_chars:
            assert char in data["characters"], f"Character '{char}' should be in characters list"
        print(f"Voice characters: {data['characters']}")
    
    def test_voice_status_has_styles(self):
        """Test /api/voice/status returns voice styles (natural, dominant, whisper)"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "styles" in data, "Response should have 'styles' field"
        assert isinstance(data["styles"], list), "Styles should be a list"
        # Should have natural, dominant, whisper
        expected_styles = ["natural", "dominant", "whisper"]
        for style in expected_styles:
            assert style in data["styles"], f"Voice style '{style}' should be available"
        print(f"Voice styles: {data['styles']}")
    
    def test_voice_status_has_languages(self):
        """Test /api/voice/status returns multi-language support (EN/ES/FR/AR)"""
        response = requests.get(f"{BASE_URL}/api/voice/status")
        data = response.json()
        assert "languages" in data, "Response should have 'languages' field"
        assert isinstance(data["languages"], list), "Languages should be a list"
        # Should have en, es, fr, ar
        expected_languages = ["en", "es", "fr", "ar"]
        for lang in expected_languages:
            assert lang in data["languages"], f"Language '{lang}' should be supported"
        print(f"Voice languages: {data['languages']}")


class TestReactivationStatsEndpoint:
    """Reactivation stats endpoint tests - /api/reactivation/stats"""
    
    def test_reactivation_stats_returns_200(self):
        """Test /api/reactivation/stats returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Reactivation stats endpoint returned: {response.json()}")
    
    def test_reactivation_stats_has_total_users(self):
        """Test /api/reactivation/stats returns total_users count"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        data = response.json()
        assert "total_users" in data, "Response should have 'total_users' field"
        assert isinstance(data["total_users"], int), "total_users should be an integer"
        assert data["total_users"] >= 0, "total_users should be non-negative"
        print(f"Total users with selected character: {data['total_users']}")
    
    def test_reactivation_stats_has_hit_paywall(self):
        """Test /api/reactivation/stats returns hit_paywall count"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        data = response.json()
        assert "hit_paywall" in data, "Response should have 'hit_paywall' field"
        assert isinstance(data["hit_paywall"], int), "hit_paywall should be an integer"
        assert data["hit_paywall"] >= 0, "hit_paywall should be non-negative"
        print(f"Users who hit paywall: {data['hit_paywall']}")
    
    def test_reactivation_stats_has_inactive_24h(self):
        """Test /api/reactivation/stats returns inactive_24h count"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        data = response.json()
        assert "inactive_24h" in data, "Response should have 'inactive_24h' field"
        assert isinstance(data["inactive_24h"], int), "inactive_24h should be an integer"
        assert data["inactive_24h"] >= 0, "inactive_24h should be non-negative"
        print(f"Users inactive for 24h+: {data['inactive_24h']}")
    
    def test_reactivation_stats_has_reactivated_count(self):
        """Test /api/reactivation/stats returns reactivated_count"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        data = response.json()
        assert "reactivated_count" in data, "Response should have 'reactivated_count' field"
        assert isinstance(data["reactivated_count"], int), "reactivated_count should be an integer"
        assert data["reactivated_count"] >= 0, "reactivated_count should be non-negative"
        print(f"Users who received reactivation: {data['reactivated_count']}")
    
    def test_reactivation_stats_no_error(self):
        """Test /api/reactivation/stats does not return error"""
        response = requests.get(f"{BASE_URL}/api/reactivation/stats")
        data = response.json()
        assert "error" not in data, f"Response should not have 'error' field, got: {data.get('error')}"
        print("Reactivation stats returned without errors")


class TestReactivationRunEndpoint:
    """Reactivation run endpoint tests - /api/reactivation/run"""
    
    def test_reactivation_run_returns_200(self):
        """Test /api/reactivation/run returns 200 OK on POST"""
        response = requests.post(f"{BASE_URL}/api/reactivation/run")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Reactivation run endpoint returned: {response.json()}")
    
    def test_reactivation_run_returns_started_status(self):
        """Test /api/reactivation/run returns started status"""
        response = requests.post(f"{BASE_URL}/api/reactivation/run")
        data = response.json()
        assert "status" in data, "Response should have 'status' field"
        assert data["status"] == "started", f"Expected status 'started', got '{data['status']}'"
        print(f"Reactivation job status: {data['status']}")
    
    def test_reactivation_run_returns_message(self):
        """Test /api/reactivation/run returns message"""
        response = requests.post(f"{BASE_URL}/api/reactivation/run")
        data = response.json()
        assert "message" in data, "Response should have 'message' field"
        assert "queued" in data["message"].lower() or "reactivation" in data["message"].lower(), \
            f"Message should indicate job queued, got: {data['message']}"
        print(f"Reactivation message: {data['message']}")
    
    def test_reactivation_run_method_not_allowed_get(self):
        """Test /api/reactivation/run returns 405 on GET"""
        response = requests.get(f"{BASE_URL}/api/reactivation/run")
        assert response.status_code == 405, f"Expected 405 Method Not Allowed for GET, got {response.status_code}"
        print("GET method correctly rejected for /api/reactivation/run")


class TestHealthEndpointReactivation:
    """Health endpoint tests (verify still working after P1 changes)"""
    
    def test_health_returns_200(self):
        """Test /api/health returns 200 OK"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"Health endpoint returned: {response.json()}")
    
    def test_health_returns_healthy_status(self):
        """Test /api/health returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert "status" in data, "Response should have 'status' field"
        assert data["status"] == "healthy", f"Expected status 'healthy', got '{data['status']}'"
        print(f"Health status: {data['status']}")
    
    def test_health_shows_telegram_configured(self):
        """Test /api/health shows telegram_configured flag"""
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        assert "telegram_configured" in data, "Response should have 'telegram_configured' field"
        assert data["telegram_configured"] == True, "Telegram should be configured"
        print(f"Telegram configured: {data['telegram_configured']}")


class TestVoicePreferenceEndpoint:
    """Voice preference endpoint tests - /api/user/{telegram_id}/voice-preference"""
    
    def test_set_voice_preference_natural(self):
        """Test setting voice preference to natural"""
        test_telegram_id = "TEST_voice_user_123"
        response = requests.post(
            f"{BASE_URL}/api/user/{test_telegram_id}/voice-preference",
            params={"preference": "natural"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "updated", f"Expected status 'updated', got '{data.get('status')}'"
        assert data.get("voice_preference") == "natural", f"Expected preference 'natural', got '{data.get('voice_preference')}'"
        print(f"Voice preference set to natural: {data}")
    
    def test_set_voice_preference_dominant(self):
        """Test setting voice preference to dominant"""
        test_telegram_id = "TEST_voice_user_124"
        response = requests.post(
            f"{BASE_URL}/api/user/{test_telegram_id}/voice-preference",
            params={"preference": "dominant"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("voice_preference") == "dominant"
        print(f"Voice preference set to dominant: {data}")
    
    def test_set_voice_preference_whisper(self):
        """Test setting voice preference to whisper"""
        test_telegram_id = "TEST_voice_user_125"
        response = requests.post(
            f"{BASE_URL}/api/user/{test_telegram_id}/voice-preference",
            params={"preference": "whisper"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("voice_preference") == "whisper"
        print(f"Voice preference set to whisper: {data}")
    
    def test_set_voice_preference_invalid(self):
        """Test setting invalid voice preference returns 400"""
        test_telegram_id = "TEST_voice_user_126"
        response = requests.post(
            f"{BASE_URL}/api/user/{test_telegram_id}/voice-preference",
            params={"preference": "invalid_style"}
        )
        assert response.status_code == 400, f"Expected 400 for invalid preference, got {response.status_code}"
        print(f"Invalid preference correctly rejected with 400")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
