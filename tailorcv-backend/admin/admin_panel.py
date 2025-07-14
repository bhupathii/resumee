#!/usr/bin/env python3
"""
TailorCV Admin Panel - Simple CLI tool for managing payments and users
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

class AdminPanel:
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("❌ Error: Supabase credentials not found in environment variables")
            sys.exit(1)
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
    def show_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("         TailorCV Admin Panel")
        print("="*50)
        print("1. View pending payments")
        print("2. Approve payment")
        print("3. Reject payment")
        print("4. View user statistics")
        print("5. View recent generations")
        print("6. Search user by email")
        print("7. Export data")
        print("8. Exit")
        print("="*50)
        
    def view_pending_payments(self):
        """View all pending payments"""
        try:
            response = self.client.table('payments').select('*').eq('status', 'pending').order('created_at', desc=True).execute()
            
            if not response.data:
                print("✅ No pending payments found")
                return
                
            print(f"\n📋 Pending Payments ({len(response.data)})")
            print("-" * 80)
            
            for payment in response.data:
                print(f"ID: {payment['id']}")
                print(f"Email: {payment['email']}")
                print(f"Amount: ₹{payment['amount']}")
                print(f"Screenshot: {payment['screenshot_url']}")
                print(f"Created: {payment['created_at']}")
                print("-" * 80)
                
        except Exception as e:
            print(f"❌ Error fetching pending payments: {e}")
    
    def approve_payment(self):
        """Approve a payment by ID"""
        payment_id = input("Enter payment ID to approve: ").strip()
        
        if not payment_id:
            print("❌ Payment ID cannot be empty")
            return
            
        try:
            # Get payment details
            payment_response = self.client.table('payments').select('*').eq('id', payment_id).execute()
            
            if not payment_response.data:
                print("❌ Payment not found")
                return
                
            payment = payment_response.data[0]
            email = payment['email']
            
            # Update payment status
            self.client.table('payments').update({
                'status': 'approved',
                'updated_at': datetime.now().isoformat()
            }).eq('id', payment_id).execute()
            
            # Update or create user with premium status
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
                    'ip': '0.0.0.0',  # Will be updated on first use
                    'is_premium': True,
                    'upgraded_at': datetime.now().isoformat(),
                    'generation_count': 0
                }).execute()
            
            print(f"✅ Payment approved successfully for {email}")
            print("📧 Consider sending a confirmation email to the user")
            
        except Exception as e:
            print(f"❌ Error approving payment: {e}")
    
    def run(self):
        """Main application loop"""
        print("🚀 TailorCV Admin Panel Starting...")
        
        # Test connection
        try:
            self.client.table('users').select('count').limit(1).execute()
            print("✅ Connected to Supabase successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            sys.exit(1)
        
        while True:
            self.show_menu()
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self.view_pending_payments()
            elif choice == '2':
                self.approve_payment()
            elif choice == '8':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    admin = AdminPanel()
    admin.run()