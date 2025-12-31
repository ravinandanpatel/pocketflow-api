import requests
import random
from datetime import datetime, timedelta

# CONFIGURATION
API_URL = "http://127.0.0.1:8000"
USERNAME = "test_user"
PASSWORD = "test_password"

def run_automation():
    print(f"🤖 Starting Automation for user: {USERNAME}...")

    # STEP 1: REGISTER (If user doesn't exist)
    # We try to create the user. If they already exist, the server returns 400, which we ignore.
    register_data = {"username": USERNAME, "hashed_password": PASSWORD}
    requests.post(f"{API_URL}/register", json=register_data)

    # STEP 2: LOGIN (Get the Access Token)
    # This is like showing your ID to get a Hotel Key Card.
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = requests.post(f"{API_URL}/token", data=login_data)

    if response.status_code != 200:
        print(f"❌ Login Failed! Reason: {response.text}")
        return
    
    # Extract the token from the response
    token = response.json()["access_token"]
    print("✅ Login Successful! Token acquired.")

    # STEP 3: PREPARE DATA
    # We attach the 'Bearer Token' to our headers.
    headers = {"Authorization": f"Bearer {token}"}
    
    transactions = [
        {"title": "December Salary", "amount": 50000.0, "category": "Salary", "type": "income"},
        {"title": "Dominos Pizza", "amount": 650.0, "category": "Food", "type": "expense"},
        {"title": "Metro Recharge", "amount": 500.0, "category": "Travel", "type": "expense"},
        {"title": "Netflix Subscription", "amount": 199.0, "category": "Entertainment", "type": "expense"},
        {"title": "Udemy Course", "amount": 499.0, "category": "Education", "type": "expense"},
    ]

    # STEP 4: SEND DATA TO API
    print("🚀 Adding Transactions...")
    for t in transactions:
        # We send the JSON data AND the Headers (Security Pass)
        res = requests.post(f"{API_URL}/transactions/", json=t, headers=headers)
        
        if res.status_code == 200:
            print(f"   + Added: {t['title']}")
        else:
            print(f"   - Failed: {t['title']} (Error: {res.text})")

    print("\n✨ Automation Complete! Check your Dashboard.")

if __name__ == "__main__":
    run_automation()


# run with --> " python populate.py "