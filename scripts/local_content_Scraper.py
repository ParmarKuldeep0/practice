import re
import socket
import csv
import json
from datetime import datetime
from pathlib import Path

class PureEmailValidator:
    def __init__(self):
        self.results = []
        self.disposable_domains = [
            '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
            'mailinator.com', 'yopmail.com', 'temp-mail.org'
        ]

    def validate_email_format(self, email):
        """Pure email format validation - no external calls"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def check_domain_exists(self, email):
        """Check if domain exists using local DNS lookup"""
        try:
            domain = email.split('@')[1]
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def is_disposable_email(self, email):
        """Check against local list of disposable email domains"""
        domain = email.split('@')[1].lower()
        return domain in self.disposable_domains

    def validate_local_signups(self, csv_file='email_signups.csv'):
        """Process email signups from local CSV file"""
        if not Path(csv_file).exists():
            print(f"❌ File not found: {csv_file}")
            print("💡 Create email_signups.csv with columns: email,name,signup_date,source")

            # Create sample file
            sample_data = [
                ['email', 'name', 'signup_date', 'source'],
                ['user@example.com', 'Sample User', '2025-09-14', 'landing_page']
            ]
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(sample_data)
            print(f"✅ Created sample file: {csv_file}")
            return []

        results = []
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)

            for row in reader:
                email = row.get('email', '').strip().lower()
                if not email:
                    continue

                validation = {
                    'email': email,
                    'name': row.get('name', ''),
                    'signup_date': row.get('signup_date', ''),
                    'source': row.get('source', ''),
                    'format_valid': self.validate_email_format(email),
                    'domain_exists': self.check_domain_exists(email),
                    'is_disposable': self.is_disposable_email(email),
                    'processed_at': datetime.now().isoformat()
                }

                # Overall validity
                validation['is_valid'] = (
                    validation['format_valid'] and
                    validation['domain_exists'] and
                    not validation['is_disposable']
                )

                results.append(validation)
                status = "✅ VALID" if validation['is_valid'] else "❌ INVALID"
                print(f"{status}: {email}")

        # Save results locally
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f'validated_emails_{timestamp}.csv'

        with open(output_file, 'w', newline='') as f:
            if results:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)

        # Summary
        valid_count = sum(1 for r in results if r['is_valid'])
        print(f"\n📊 VALIDATION SUMMARY:")
        print(f"Total processed: {len(results)}")
        print(f"Valid emails: {valid_count}")
        print(f"Invalid emails: {len(results) - valid_count}")
        print(f"Results saved: {output_file}")

        return results

if __name__ == "__main__":
    validator = PureEmailValidator()
    validator.validate_local_signups()
