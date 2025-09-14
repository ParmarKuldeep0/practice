import pandas as pd
import requests
import re
import os
from datetime import datetime
import json

class EmailValidator:
    def __init__(self, api_url=None):
        self.api_url = api_url or os.getenv('MERN_API_URL', 'http://localhost:5000')

    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def check_domain_exists(self, email):
        """Basic domain validation"""
        domain = email.split('@')[1]
        common_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        return domain in common_domains or '.' in domain

    def process_email_signups(self):
        """Process new email signups from various sources"""

        # Sample data - replace with your actual data source
        sample_emails = [
            'test1@gmail.com',
            'invalid-email',
            'user@yahoo.com',
            'business@example.com'
        ]

        validated_emails = []

        for email in sample_emails:
            if self.validate_email(email) and self.check_domain_exists(email):
                validated_emails.append({
                    'email': email,
                    'validated_at': datetime.now().isoformat(),
                    'status': 'valid',
                    'source': 'landing_page'
                })

        # Send to your MERN backend (when it's ready)
        try:
            if self.api_url and validated_emails:
                response = requests.post(
                    f'{self.api_url}/api/leads',
                    json={'emails': validated_emails},
                    timeout=10
                )
                print(f"✅ Sent {len(validated_emails)} validated emails to backend")
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Could not connect to backend: {e}")

        # Save locally as backup
        with open('validated_emails.json', 'w') as f:
            json.dump(validated_emails, f, indent=2)

        print(f"📧 Processed {len(validated_emails)} valid emails")
        return validated_emails

if __name__ == "__main__":
    validator = EmailValidator()
    validator.process_email_signups()
