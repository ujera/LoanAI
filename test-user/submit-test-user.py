#!/usr/bin/env python3
"""
Test User Submission Script (Python version)
Sends a test loan application to the backend API
"""

import json
import requests
from typing import Dict, Any

# Test user data
test_user_data: Dict[str, Any] = {
    # Personal Information
    "firstName": "Luka",
    "lastName": "Narsia",
    "personalId": "0XX010XXXX",
    "gender": "male",
    "birthYear": "1990",
    "phone": "+995555123456",
    "address": "Tbilisi, Georgia",
    
    # Education
    "educationLevel": "bachelor",
    "university": "Georgian Technical University",
    
    # Employment
    "employmentStatus": "employed",
    "companyName": "GeoTech Solutions LLC",
    "monthlySalary": "3500",
    "experienceYears": "5",
    
    # Loan Details
    "loanPurpose": "business",
    "loanAmount": "15000",
    "loanDuration": "24",
    "additionalInfo": "Software Engineer at GeoTech Solutions LLC. Payment date: March 5, 2025. Currency: GEL",
    
    # Documents (if you have uploaded them)
    # "bankStatementUrl": "path/to/bank/statement",
    # "salaryStatementUrl": "path/to/salary/statement",
}


def submit_test_user():
    """Submit test user data to the backend API"""
    backend_url = 'http://localhost:3000/api/loan-application'
    
    print('Submitting test user to backend...')
    print(f'Backend URL: {backend_url}')
    print('\nTest User Data:')
    print(json.dumps(test_user_data, indent=2))
    print('\n' + '=' * 50)
    
    try:
        response = requests.post(
            backend_url,
            json=test_user_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response_data = response.json()
        
        print(f'\nResponse Status: {response.status_code}')
        print('Response Data:')
        print(json.dumps(response_data, indent=2))
        
        if response.ok:
            print('\n✅ SUCCESS! Test user submitted successfully!')
            customer_id = response_data.get('customerId')
            if customer_id:
                print(f'Customer ID: {customer_id}')
                print('\nYou can check the application at:')
                print(f'http://localhost:3000/api/loan-application?customerId={customer_id}')
        else:
            print('\n❌ FAILED! Submission failed.')
            if 'error' in response_data:
                print(f"Error: {response_data['error']}")
            if 'details' in response_data:
                print(f"Details: {response_data['details']}")
                
    except requests.exceptions.ConnectionError:
        print('\n❌ ERROR! Failed to connect to backend.')
        print('\nMake sure:')
        print('1. Backend server is running (npm run dev)')
        print('2. Cloud SQL Proxy is running (./start-proxy.sh)')
        print('3. Backend is accessible at http://localhost:3000')
    except requests.exceptions.Timeout:
        print('\n❌ ERROR! Request timed out.')
        print('The backend might be slow or unresponsive.')
    except Exception as e:
        print(f'\n❌ ERROR! Failed to submit test user:')
        print(f'{type(e).__name__}: {str(e)}')
        print('\nMake sure:')
        print('1. Backend server is running (npm run dev)')
        print('2. Cloud SQL Proxy is running (./start-proxy.sh)')
        print('3. Database is properly configured')


if __name__ == '__main__':
    submit_test_user()
