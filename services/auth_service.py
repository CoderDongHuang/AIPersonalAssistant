"""
Google OAuth Authentication Service

Handles Google API authentication and authorization management
Supports Calendar API and Gmail API authentication
"""

import os
import pickle
from pathlib import Path
from typing import Optional, List
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from loguru import logger


class AuthService:
    """Google OAuth Authentication Service"""

    # Google API required scopes
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]

    def __init__(self, credentials_file: str = "credentials.json",
                 token_file: str = "token.pickle"):
        """
        Initialize authentication service

        Args:
            credentials_file: OAuth credentials file path
            token_file: Token cache file path
        """
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)
        self._credentials: Optional[Credentials] = None

        logger.info("AuthService initialized (Google)")
        logger.debug(f"Credentials file: {self.credentials_file}")
        logger.debug(f"Token file: {self.token_file}")

    def authenticate(self) -> Credentials:
        """
        Execute authentication flow

        Returns:
            Credentials: Google OAuth credentials object

        Raises:
            FileNotFoundError: credentials.json not found
            Exception: Authentication failed
        """
        if not self.credentials_file.exists():
            logger.error(f"❌ credentials.json not found: {self.credentials_file}")
            logger.error("Please download from Google Cloud Console")
            raise FileNotFoundError(
                f"Credentials file not found: {self.credentials_file}\n"
                "Please download it from Google Cloud Console"
            )

        credentials = self._load_cached_token()

        if credentials and self._is_token_valid(credentials):
            logger.info("✅ Using cached token")
            self._credentials = credentials
            return credentials

        logger.info("🔐 Starting OAuth authentication flow...")
        credentials = self._perform_oauth_flow()

        self._save_token(credentials)

        self._credentials = credentials
        logger.info("✅ OAuth authentication successful")

        return credentials

    def get_credentials(self) -> Optional[Credentials]:
        """Get current credentials (if authenticated)"""
        if self._credentials is None:
            logger.warning("⚠️  Not authenticated, call authenticate() first")
        return self._credentials

    def refresh_token_if_needed(self) -> bool:
        """Refresh token if needed"""
        if self._credentials is None:
            return False

        if not self._credentials.valid:
            logger.info("🔄 Token expired, refreshing...")
            try:
                self._credentials.refresh(Request())
                self._save_token(self._credentials)
                logger.info("✅ Token refreshed")
                return True
            except Exception as e:
                logger.error(f"❌ Token refresh failed: {e}")
                return False

        return True

    def revoke_access(self):
        """Revoke authorization (delete cached token)"""
        if self.token_file.exists():
            self.token_file.unlink()
            logger.info("🗑️  Authorization revoked, token deleted")

        self._credentials = None

    def _load_cached_token(self) -> Optional[Credentials]:
        """Load token from cache file"""
        if not self.token_file.exists():
            logger.debug("No cached token file found")
            return None

        try:
            with open(self.token_file, 'rb') as token_file:
                credentials = pickle.load(token_file)
                logger.debug("Successfully loaded cached token")
                return credentials
        except Exception as e:
            logger.warning(f"⚠️  Failed to load cached token: {e}")
            return None

    def _is_token_valid(self, credentials: Credentials) -> bool:
        """Check if token is valid"""
        if credentials is None:
            return False

        if not credentials.valid:
            logger.debug("Token invalid or expired")
            return False

        if credentials.scopes != self.SCOPES:
            logger.warning("⚠️  Token scope mismatch")
            return False

        logger.debug("Token validation passed")
        return True

    def _perform_oauth_flow(self) -> Credentials:
        """Execute OAuth authorization flow"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                self.SCOPES
            )

            logger.info("🌐 Opening browser for authorization...")
            logger.info("Please login to Google account and authorize")

            credentials = flow.run_local_server(
                port=0,
                open_browser=True
            )

            logger.info("✅ Browser authorization completed")
            return credentials

        except Exception as e:
            logger.error(f"❌ OAuth authentication failed: {e}")
            raise

    def _save_token(self, credentials: Credentials):
        """Save token to cache file"""
        try:
            with open(self.token_file, 'wb') as token_file:
                pickle.dump(credentials, token_file)

            logger.info(f"💾 Token saved to: {self.token_file}")

            if os.name != 'nt':
                os.chmod(self.token_file, 0o600)

        except Exception as e:
            logger.error(f"❌ Failed to save token: {e}")
            raise

    def get_user_email(self) -> Optional[str]:
        """Get authorized user's email address"""
        if self._credentials is None:
            logger.warning("⚠️  Not authenticated")
            return None

        if hasattr(self._credentials, 'id_token'):
            import jwt
            try:
                decoded = jwt.decode(
                    self._credentials.id_token,
                    options={"verify_signature": False}
                )
                return decoded.get('email')
            except Exception as e:
                logger.warning(f"⚠️  Failed to parse user email: {e}")

        return None


# Global auth service instance
auth_service = AuthService()