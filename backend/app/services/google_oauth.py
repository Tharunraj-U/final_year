"""
Google OAuth Service for authentication.
"""

import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


class GoogleOAuthService:
    def __init__(self):
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.token_info_url = 'https://oauth2.googleapis.com/tokeninfo'
    
    def verify_token(self, token: str) -> dict:
        """
        Verify a Google OAuth token and return user info.
        
        Args:
            token: The ID token from Google Sign-In
            
        Returns:
            dict with user info (email, name, picture, etc.) or None if invalid
        """
        try:
            # Verify the token using Google's library
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer')
            
            # Token is valid, return user info
            return {
                'google_id': idinfo['sub'],
                'email': idinfo.get('email'),
                'email_verified': idinfo.get('email_verified', False),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'given_name': idinfo.get('given_name'),
                'family_name': idinfo.get('family_name')
            }
            
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def verify_access_token(self, access_token: str) -> dict:
        """
        Verify a Google access token and get user info.
        Alternative method using tokeninfo endpoint.
        """
        try:
            # Get user info from Google
            response = requests.get(
                'https://www.googleapis.com/oauth2/v3/userinfo',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code != 200:
                print(f"Failed to get user info: {response.status_code}")
                return None
            
            user_info = response.json()
            
            return {
                'google_id': user_info.get('sub'),
                'email': user_info.get('email'),
                'email_verified': user_info.get('email_verified', False),
                'name': user_info.get('name'),
                'picture': user_info.get('picture'),
                'given_name': user_info.get('given_name'),
                'family_name': user_info.get('family_name')
            }
            
        except Exception as e:
            print(f"Error verifying access token: {e}")
            return None


# Singleton instance
google_oauth_service = GoogleOAuthService()
