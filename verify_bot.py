
import requests
import json
import subprocess
import time

BASE_URL = "http://localhost:8000/api"

USERS = [
    {"username": "alice", "password": "password", "profile": "CADRE", "question": "Comment déclarer des heures supplémentaires ?", "expected_part": "Via le manager"},
    {"username": "bob", "password": "password", "profile": "CDI", "question": "Comment poser un congé annuel ?", "expected_part": "via le portail RH"},
    {"username": "david", "password": "password", "profile": "STAGIAIRE", "question": "Ai-je accès à la cantine ?", "expected_part": "Oui les stagiaires y ont accès"},
]

def get_token(username, password):
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            return response.json()["access_token"]
        return None
    except:
        return None

def test_chat(token, message):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/chat", json={"message": message}, headers=headers)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

print("=== Starting Verification Tests ===")

results = []

for user in USERS:
    print(f"\nTesting User: {user['username']} ({user['profile']})")
    token = get_token(user['username'], user['password'])
    
    if not token:
        print("❌ Login Failed")
        results.append(f"User {user['username']}: Login Failed")
        continue
        
    print(f"✅ Login Success")
    
    answer_data = test_chat(token, user['question'])
    
    if answer_data:
        answer_text = answer_data['answer']
        print(f"Q: {user['question']}")
        print(f"A: {answer_text}")
        
        if user['expected_part'].lower() in answer_text.lower():
            print("✅ Answer Verified (Contains expected text)")
            results.append(f"User {user['username']}: RAG Verified")
        else:
            print(f"❌ Answer Mismatch. Expected '{user['expected_part']}'")
            results.append(f"User {user['username']}: RAG Mismatch")
            
        # Check for strict "Pour répondre à votre question" prefix if RAG
        if "Pour répondre à votre question" in answer_text:
             print("✅ Strict Mode Verified")
    else:
        print("❌ Chat Request Failed")
        results.append(f"User {user['username']}: Chat Failed")

print("\n=== Verification Summary ===")
for r in results:
    print(r)
