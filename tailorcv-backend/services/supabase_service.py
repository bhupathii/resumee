import os
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client

class SupabaseService:
    def __init__(self):
        self.url = os.environ.get('SUPABASE_URL')
        self.key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be configured")
            
        self.client: Client = create_client(self.url, self.key)
    
    def check_user_premium_status(self, email: Optional[str], ip_address: str) -> Dict[str, Any]:
        """
        Check if user has premium access based on email or IP
        """
        try:
            # First check by email if provided
            if email:
                response = self.client.table('payments').select('*').eq('email', email).eq('status', 'approved').execute()
                if response.data:
                    return {
                        'is_premium': True,
                        'email': email,
                        'approved_at': response.data[0].get('updated_at')
                    }
            
            # Check by IP address
            response = self.client.table('users').select('*').eq('ip', ip_address).execute()
            if response.data:
                user_data = response.data[0]
                return {
                    'is_premium': user_data.get('is_premium', False),
                    'generation_count': user_data.get('generation_count', 0),
                    'last_generated': user_data.get('last_generated')
                }
            
            return {
                'is_premium': False,
                'generation_count': 0,
                'last_generated': None
            }
            
        except Exception as e:
            print(f"Error checking user premium status: {str(e)}")
            return {
                'is_premium': False,
                'generation_count': 0,
                'last_generated': None
            }
    
    def create_payment_record(self, payment_data: Dict[str, Any]) -> None:
        """
        Create a new payment record in the database
        """
        try:
            self.client.table('payments').insert(payment_data).execute()
        except Exception as e:
            raise Exception(f"Failed to create payment record: {str(e)}")
    
    def log_generation(self, email: Optional[str], ip_address: str, job_description_snippet: str) -> None:
        """
        Log a resume generation event
        """
        try:
            # Update or create user record
            user_data = {
                'email': email,
                'ip': ip_address,
                'last_generated': datetime.now().isoformat(),
                'generation_count': 1
            }
            
            # Check if user exists
            response = self.client.table('users').select('*').eq('ip', ip_address).execute()
            
            if response.data:
                # Update existing user
                existing_user = response.data[0]
                user_data['generation_count'] = existing_user.get('generation_count', 0) + 1
                
                self.client.table('users').update(user_data).eq('id', existing_user['id']).execute()
            else:
                # Create new user
                self.client.table('users').insert(user_data).execute()
            
            # Log the generation event
            generation_log = {
                'email': email,
                'ip': ip_address,
                'job_description_snippet': job_description_snippet,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client.table('generations').insert(generation_log).execute()
            
        except Exception as e:
            print(f"Error logging generation: {str(e)}")
    
    def upload_resume(self, file_path: str, filename: str) -> str:
        """
        Upload resume PDF to Supabase storage
        """
        try:
            with open(file_path, 'rb') as file:
                response = self.client.storage.from_('resumes').upload(
                    path=filename,
                    file=file,
                    file_options={"content-type": "application/pdf"}
                )
            
            # Get public URL
            public_url = self.client.storage.from_('resumes').get_public_url(filename)
            return public_url
            
        except Exception as e:
            raise Exception(f"Failed to upload resume to storage: {str(e)}")
    
    def upload_payment_screenshot(self, file_path: str, filename: str) -> str:
        """
        Upload payment screenshot to Supabase storage
        """
        try:
            with open(file_path, 'rb') as file:
                response = self.client.storage.from_('payments').upload(
                    path=filename,
                    file=file,
                    file_options={"content-type": "image/jpeg"}
                )
            
            # Get public URL
            public_url = self.client.storage.from_('payments').get_public_url(filename)
            return public_url
            
        except Exception as e:
            raise Exception(f"Failed to upload payment screenshot to storage: {str(e)}")
    
    def approve_payment(self, payment_id: str) -> None:
        """
        Approve a payment (admin function)
        """
        try:
            # Update payment status
            self.client.table('payments').update({
                'status': 'approved',
                'updated_at': datetime.now().isoformat()
            }).eq('id', payment_id).execute()
            
            # Get payment details
            payment_response = self.client.table('payments').select('*').eq('id', payment_id).execute()
            
            if payment_response.data:
                payment = payment_response.data[0]
                email = payment.get('email')
                
                # Find and update user record
                if email:
                    user_response = self.client.table('users').select('*').eq('email', email).execute()
                    
                    if user_response.data:
                        # Update existing user
                        self.client.table('users').update({
                            'is_premium': True,
                            'upgraded_at': datetime.now().isoformat()
                        }).eq('email', email).execute()
                    else:
                        # Create new premium user
                        self.client.table('users').insert({
                            'email': email,
                            'is_premium': True,
                            'upgraded_at': datetime.now().isoformat(),
                            'generation_count': 0
                        }).execute()
            
        except Exception as e:
            raise Exception(f"Failed to approve payment: {str(e)}")
    
    def get_pending_payments(self) -> list:
        """
        Get all pending payments for admin review
        """
        try:
            response = self.client.table('payments').select('*').eq('status', 'pending').order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            raise Exception(f"Failed to get pending payments: {str(e)}")
    
    def initialize_tables(self) -> None:
        """
        Initialize database tables (run once during setup)
        """
        try:
            # This would be handled by Supabase migrations in production
            # For now, we'll create tables manually in Supabase dashboard
            pass
        except Exception as e:
            print(f"Error initializing tables: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test if Supabase connection is working
        """
        try:
            response = self.client.table('users').select('count').limit(1).execute()
            return True
        except Exception:
            return False