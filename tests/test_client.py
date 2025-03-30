import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from strava_client.client import StravaClient
from strava_client.models.settings import StravaSettings
from strava_client.constants import DEFAULT_SCOPES
from strava_client.enums.auth import StravaScope
from strava_client.models.requests import StravaGetTokenResponse


@pytest.fixture
def mock_settings():
    """Fixture to mock the StravaSettings"""
    settings = MagicMock(spec=StravaSettings)
    settings.client_id = 0
    settings.client_secret = "test_client_secret"
    settings.refresh_token = "test_refresh_token"
    settings.access_token = "test_access_token"
    settings.expires_at = int((datetime.now() + timedelta(hours=1)).timestamp())
    return settings


@pytest.fixture
def mock_expired_settings():
    """Fixture to mock expired StravaSettings"""
    settings = MagicMock(spec=StravaSettings)
    settings.client_id = 0
    settings.client_secret = "test_client_secret"
    settings.refresh_token = "test_refresh_token"
    settings.access_token = "test_access_token"
    settings.expires_at = int((datetime.now() - timedelta(hours=1)).timestamp())
    return settings


@pytest.fixture
def mock_new_settings():
    """Fixture to mock new StravaSettings without refresh token"""
    settings = MagicMock(spec=StravaSettings)
    settings.client_id = "test_client_id"
    settings.client_secret = "test_client_secret"
    settings.refresh_token = None
    settings.access_token = None
    settings.expires_at = 0
    return settings


@pytest.fixture
def mock_strava_response():
    """Fixture to mock the Strava token response"""
    return StravaGetTokenResponse(
        access_token="new_access_token",
        refresh_token="new_refresh_token",
        expires_at=int((datetime.now() + timedelta(hours=1)).timestamp()),
    )


@pytest.fixture
def mock_activities():
    """Fixture to mock activities response"""
    return [
        {
            "id": "1234567890",
            "name": "Morning Run",
            "distance": 5000,
            "moving_time": 1800,
            "elapsed_time": 1900,
            "start_date": "2023-01-01T10:00:00Z",
            "start_date_local": "2023-01-01T10:00:00Z",
            "type": "Run",
        },
        {
            "id": "9876543210",
            "name": "Evening Ride",
            "distance": 20000,
            "moving_time": 3600,
            "elapsed_time": 3700,
            "start_date": "2023-01-02T18:00:00Z",
            "start_date_local": "2023-01-02T18:00:00Z",
            "type": "Ride",
        },
    ]


class TestStravaClient:
    @patch("strava_client.client.StravaSettings")
    def test_init_with_default_scopes(self, mock_settings_class):
        """Test initialization with default scopes"""
        mock_settings_class.return_value = MagicMock()
        client = StravaClient()

        assert client.scopes == DEFAULT_SCOPES
        assert hasattr(client, "settings")

    @patch("strava_client.client.StravaSettings")
    def test_init_with_custom_scopes(self, mock_settings_class):
        """Test initialization with custom scopes"""
        mock_settings_class.return_value = MagicMock()
        custom_scopes = [StravaScope.PROFILE_READ_ALL, StravaScope.ACTIVITY_WRITE]
        client = StravaClient(scopes=custom_scopes)

        assert client.scopes == custom_scopes
        assert hasattr(client, "settings")

    @patch("strava_client.client.StravaSettings")
    def test_init_with_string_scopes(self, mock_settings_class):
        """Test initialization with string scopes"""
        mock_settings_class.return_value = MagicMock()
        string_scopes = ["read", "activity:read"]
        expected_scopes = [StravaScope.READ, StravaScope.ACTIVITY_READ]
        client = StravaClient(scopes=string_scopes)

        assert client.scopes == expected_scopes
        assert hasattr(client, "settings")

    @patch("strava_client.client.StravaClient._refresh_token")
    @patch("strava_client.client.StravaClient._update_settings_and_dump")
    @patch("strava_client.client.StravaSettings")
    def test_verify_token_expired(
        self,
        mock_settings_class,
        mock_update_settings,
        mock_refresh_token,
        mock_expired_settings,
        mock_strava_response,
    ):
        """Test _verify_token when token is expired"""
        mock_settings_class.return_value = mock_expired_settings
        mock_refresh_token.return_value = mock_strava_response

        client = StravaClient()
        client._verify_token()

        mock_refresh_token.assert_called_once()
        mock_update_settings.assert_called_once_with(mock_strava_response)

    @patch("strava_client.client.requests.post")
    @patch("strava_client.client.StravaSettings")
    def test_refresh_token(
        self, mock_settings_class, mock_post, mock_settings, mock_strava_response
    ):
        """Test _refresh_token method"""
        mock_settings_class.return_value = mock_settings

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_strava_response.model_dump()
        mock_post.return_value = mock_response

        client = StravaClient()
        response = client._refresh_token()

        mock_post.assert_called_once()
        assert isinstance(response, StravaGetTokenResponse)
        assert response.access_token == "new_access_token"
        assert response.refresh_token == "new_refresh_token"

    @patch("strava_client.client.StravaSettings")
    def test_update_settings_and_dump(
        self, mock_settings_class, mock_settings, mock_strava_response
    ):
        """Test _update_settings_and_dump method"""
        mock_settings_class.return_value = mock_settings

        client = StravaClient()
        client._update_settings_and_dump(mock_strava_response)

        assert client.settings.access_token == "new_access_token"
        assert client.settings.refresh_token == "new_refresh_token"
        assert client.settings.expires_at == mock_strava_response.expires_at
        client.settings.dump.assert_called_once()

    @patch("strava_client.client.StravaClient._request_auth_code")
    @patch("strava_client.client.StravaClient._get_access_token")
    @patch("strava_client.client.StravaClient._update_settings_and_dump")
    @patch("strava_client.client.StravaSettings")
    def test_verify_initialization_new_client(
        self,
        mock_settings_class,
        mock_update_settings,
        mock_get_access_token,
        mock_request_auth_code,
        mock_new_settings,
        mock_strava_response,
    ):
        """Test _verify_initialization for a new client"""
        mock_settings_class.return_value = mock_new_settings
        mock_request_auth_code.return_value = "test_auth_code"
        mock_get_access_token.return_value = mock_strava_response

        StravaClient()

        mock_request_auth_code.assert_called_once()
        mock_get_access_token.assert_called_once_with("test_auth_code")
        mock_update_settings.assert_called_once_with(mock_strava_response)

    @patch("strava_client.client.webbrowser.open")
    @patch("builtins.input")
    @patch("strava_client.client.StravaSettings")
    def test_request_auth_code(
        self, mock_settings_class, mock_input, mock_webbrowser_open, mock_settings
    ):
        """Test _request_auth_code method"""
        mock_settings_class.return_value = mock_settings
        mock_input.return_value = (
            "http://localhost/exchange_token?code=test_auth_code&scope=read"
        )

        client = StravaClient()
        auth_code = client._request_auth_code()

        mock_webbrowser_open.assert_called_once()
        mock_input.assert_called_once()
        assert auth_code == "test_auth_code"

    @patch("strava_client.client.requests.post")
    @patch("strava_client.client.StravaSettings")
    def test_get_access_token(
        self, mock_settings_class, mock_post, mock_settings, mock_strava_response
    ):
        """Test _get_access_token method"""
        mock_settings_class.return_value = mock_settings

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_strava_response.model_dump()
        mock_post.return_value = mock_response

        client = StravaClient()
        response = client._get_access_token("test_auth_code")

        mock_post.assert_called_once()
        assert isinstance(response, StravaGetTokenResponse)
        assert response.access_token == "new_access_token"
        assert response.refresh_token == "new_refresh_token"
