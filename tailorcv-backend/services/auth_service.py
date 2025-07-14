import os
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from services.supabase_service import SupabaseService

class AuthService:
    def __init__(self):
        self.supabase_service = SupabaseService()
        self.google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.jwt_secret = os.environ.get('JWT_SECRET', 'your-jwt-secret-key')
        self.session_duration_hours = 24 * 7  # 7 days
        
    def verify_google_token(self, google_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google OAuth token and extract user information
        """
        try:
            if not self.google_client_id:
                print("Google Client ID not configured")
                return None
                
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                google_token, 
                google_requests.Request(), 
                self.google_client_id
            )
            
            # Check if the token is for our client ID
            if idinfo['aud'] != self.google_client_id:
                print(f"Token audience mismatch. Expected: {self.google_client_id}, Got: {idinfo.get('aud')}")
                return None
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo['name'],
                'profile_picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
            
            return user_info
            
        except ValueError as e:
            print(f"Invalid Google token: {str(e)}")
            return None
        except Exception as e:
            print(f"Error verifying Google token: {str(e)}")
            return None
    
    def authenticate_user(self, google_token: str, ip_address: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user with Google token and create/update user record
        """
        try:
            # Verify Google token
            user_info = self.verify_google_token(google_token)
            if not user_info:
                return None
            
            # Check if user exists
            existing_user = self.supabase_service.client.table('users').select('*').eq('google_id', user_info['google_id']).execute()
            
            user_data = {
                'google_id': user_info['google_id'],
                'name': user_info['name'],
                'email': user_info['email'],
                'google_email': user_info['email'],
                'profile_picture': user_info['profile_picture'],
                'ip': ip_address,
                'auth_provider': 'google',
                'last_login': datetime.now().isoformat()
            }
            
            if existing_user.data:
                # Update existing user
                user_id = existing_user.data[0]['id']
                self.supabase_service.client.table('users').update(user_data).eq('id', user_id).execute()
                user_record = existing_user.data[0]
                user_record.update(user_data)
            else:
                # Create new user
                response = self.supabase_service.client.table('users').insert(user_data).execute()
                user_record = response.data[0]
                user_id = user_record['id']
                
                # Create default preferences
                self.supabase_service.client.table('user_preferences').insert({
                    'user_id': user_id,
                    'theme': 'light',
                    'email_notifications': True,
                    'preferred_template': 'professional'
                }).execute()
            
            # Create session
            session_token = self.create_session(user_id)
            
            # Return user data with session
            return {
                'user': user_record,
                'session_token': session_token,
                'expires_at': (datetime.now() + timedelta(hours=self.session_duration_hours)).isoformat()
            }
            
        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None
    
    def create_session(self, user_id: str) -> str:
        """
        Create a new session for the user
        """
        try:
            # Generate secure session token
            session_token = secrets.token_urlsafe(64)
            expires_at = datetime.now() + timedelta(hours=self.session_duration_hours)
            
            # Store session in database
            self.supabase_service.client.table('user_sessions').insert({
                'user_id': user_id,
                'session_token': session_token,
                'expires_at': expires_at.isoformat(),
                'last_accessed': datetime.now().isoformat()
            }).execute()
            
            return session_token
            
        except Exception as e:
            print(f"Error creating session: {str(e)}")
            return None
    
    def verify_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Verify session token and return user information
        """
        try:
            # Get session from database
            session_response = self.supabase_service.client.table('user_sessions').select('*, users(*)').eq('session_token', session_token).execute()
            
            if not session_response.data:
                return None
            
            session = session_response.data[0]
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(session['expires_at'].replace('Z', '+00:00'))
            if datetime.now() > expires_at.replace(tzinfo=None):
                # Delete expired session
                self.supabase_service.client.table('user_sessions').delete().eq('session_token', session_token).execute()
                return None
            
            # Update last accessed time
            self.supabase_service.client.table('user_sessions').update({
                'last_accessed': datetime.now().isoformat()
            }).eq('session_token', session_token).execute()
            
            return {
                'user': session['users'],
                'session': session
            }
            
        except Exception as e:
            print(f"Error verifying session: {str(e)}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """
        Log out user by deleting their session
        """
        try:
            self.supabase_service.client.table('user_sessions').delete().eq('session_token', session_token).execute()
            return True
        except Exception as e:
            print(f"Error logging out user: {str(e)}")
            return False
    
    def logout_all_sessions(self, user_id: str) -> bool:
        """
        Log out user from all devices by deleting all their sessions
        """
        try:
            self.supabase_service.client.table('user_sessions').delete().eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error logging out from all sessions: {str(e)}")
            return False
    
    def get_user_by_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from session token
        """
        session_data = self.verify_session(session_token)
        return session_data['user'] if session_data else None
    
    def check_premium_status_authenticated(self, user_id: str) -> Dict[str, Any]:
        """
        Check premium status for authenticated user
        """
        try:
            # Get user record
            user_response = self.supabase_service.client.table('users').select('*').eq('id', user_id).execute()
            
            if not user_response.data:
                return {'is_premium': False, 'generation_count': 0}
            
            user = user_response.data[0]
            
            # Check if user has approved payments
            if user.get('email'):
                payment_response = self.supabase_service.client.table('payments').select('*').eq('email', user['email']).eq('status', 'approved').execute()
                if payment_response.data:
                    return {
                        'is_premium': True,
                        'generation_count': user.get('generation_count', 0),
                        'last_generated': user.get('last_generated'),
                        'upgraded_at': payment_response.data[0].get('updated_at')
                    }
            
            return {
                'is_premium': user.get('is_premium', False),
                'generation_count': user.get('generation_count', 0),
                'last_generated': user.get('last_generated'),
                'upgraded_at': user.get('upgraded_at')
            }
            
        except Exception as e:
            print(f"Error checking premium status: {str(e)}")
            return {'is_premium': False, 'generation_count': 0}
    
    def increment_generation_count(self, user_id: str) -> bool:
        """
        Increment generation count for authenticated user
        """
        try:
            self.supabase_service.client.table('users').update({
                'generation_count': self.supabase_service.client.table('users').select('generation_count').eq('id', user_id).execute().data[0]['generation_count'] + 1,
                'last_generated': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            return True
        except Exception as e:
            print(f"Error incrementing generation count: {str(e)}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (called periodically)
        """
        try:
            # Delete expired sessions
            result = self.supabase_service.client.table('user_sessions').delete().lt('expires_at', datetime.now().isoformat()).execute()
            return len(result.data) if result.data else 0
        except Exception as e:
            print(f"Error cleaning up sessions: {str(e)}")
            return 0 