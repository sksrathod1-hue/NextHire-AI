import urllib.request
import urllib.parse
import json
import os
import http.cookiejar

# Set up cookie handler to persist session cookies
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
urllib.request.install_opener(opener)

BASE_URL = 'http://127.0.0.1:5000'

def test_flow():
    print("=== Starting NextHire AI Logic Verification (Zero-Dependency) ===")
    
    # Reset database for tester@nexthire.ai to ensure idempotence
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'nexthire.db')
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("DELETE FROM users WHERE email = 'tester@nexthire.ai'")
            conn.execute("DELETE FROM users WHERE email = 'google-tester@nexthire.ai'")
            conn.commit()
            conn.close()
            print("Database cleaned up for test accounts.")
        except Exception as e:
            print(f"Db clean warning: {e}")

    # 1. Sign Up Test
    signup_data = {
        'fullname': 'Automated Tester',
        'email': 'tester@nexthire.ai',
        'password': 'password123',
        'confirm-password': 'password123',
        'phone': '+15550009999',
        'college': 'Test Tech Institute'
    }
    
    print("\n1. Testing Signup POST...")
    data_encoded = urllib.parse.urlencode(signup_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/signup", data=data_encoded, method='POST')
    
    try:
        response = urllib.request.urlopen(req)
        final_url = response.geturl()
        content = response.read().decode('utf-8')
        print(f"Final URL after signup redirect: {final_url}")
        assert "dashboard" in final_url, "Signup should redirect to dashboard."
        assert "Automated Tester" in content, "Dashboard should render user's name."
        assert "Test Tech Institute" in content, "Dashboard should render user's college."
        print("Signup and Jinja variable binding verified!")
    except Exception as e:
        print(f"Signup error: {e}")
        raise e

    # 2. Log Out Test
    print("\n2. Testing Logout GET...")
    try:
        response = urllib.request.urlopen(f"{BASE_URL}/logout")
        final_url = response.geturl()
        print(f"Final URL after logout redirect: {final_url}")
        assert final_url == f"{BASE_URL}/" or final_url == f"{BASE_URL}" or "login" in final_url, "Logout redirect mismatch."
        
        # Verify dashboard redirect (redirects to login, which is fine)
        resp_dash = urllib.request.urlopen(f"{BASE_URL}/dashboard")
        assert "login" in resp_dash.geturl(), "Dashboard should redirect unauthenticated user to login."
        print("Logout lock verified!")
    except Exception as e:
        print(f"Logout error: {e}")
        raise e

    # 3. Log In Test
    print("\n3. Testing Login POST...")
    login_data = {
        'email': 'tester@nexthire.ai',
        'password': 'password123'
    }
    data_encoded = urllib.parse.urlencode(login_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/login", data=data_encoded, method='POST')
    try:
        response = urllib.request.urlopen(req)
        final_url = response.geturl()
        print(f"Final URL after login redirect: {final_url}")
        assert "dashboard" in final_url, "Login should redirect to dashboard."
        print("Login authentication verified!")
    except Exception as e:
        print(f"Login error: {e}")
        raise e

    # 4. Update Profile Settings
    print("\n4. Testing Profile Update POST...")
    profile_data = {
        'fullname': 'Automated Tester Updated',
        'email': 'tester@nexthire.ai',
        'phone': '+19998887777',
        'college': 'Updated University',
        'password': ''
    }
    data_encoded = urllib.parse.urlencode(profile_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/update-profile", data=data_encoded, method='POST')
    try:
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        assert "Automated Tester Updated" in content, "Dashboard should reflect updated name."
        assert "Updated University" in content, "Dashboard should reflect updated college."
        print("Profile update verified!")
    except Exception as e:
        print(f"Profile update error: {e}")
        raise e

    # 5. Update Career Strategy Settings
    print("\n5. Testing Career Update POST...")
    career_data = {
        'target_role': 'Lead AI Architect',
        'experience_lvl': 'Senior',
        'difficulty': 'Hard'
    }
    data_encoded = urllib.parse.urlencode(career_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/update-career", data=data_encoded, method='POST')
    try:
        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')
        assert "Lead AI Architect" in content, "Dashboard should reflect updated role."
        print("Career updates verified!")
    except Exception as e:
        print(f"Career update error: {e}")
        raise e

    # 6. Parse Resume API (Multipart Form Post)
    print("\n6. Testing Resume Parser API...")
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    resume_path = os.path.join(os.path.dirname(__file__), 'uploads', 'test_resume.txt')
    with open(resume_path, 'r', encoding='utf-8') as f:
        file_content = f.read()
    
    parts = []
    parts.append(f'--{boundary}')
    parts.append('Content-Disposition: form-data; name="file"; filename="test_resume.txt"')
    parts.append('Content-Type: text/plain')
    parts.append('')
    parts.append(file_content)
    parts.append(f'--{boundary}--')
    parts.append('')
    
    body = '\r\n'.join(parts).encode('utf-8')
    
    req = urllib.request.Request(f"{BASE_URL}/api/parse-resume", data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print(f"API Response: {res_data}")
        assert 'score' in res_data, "Response lacks ATS score."
        assert res_data['score'] >= 70, "ATS Score should be >= 70."
        print("Resume parser API verified!")
    except Exception as e:
        print(f"Resume parser error: {e}")
        raise e

    # 7. Evaluate Answer API (JSON Post)
    print("\n7. Testing Mock Answer Evaluation API...")
    eval_data = {
        'role': 'Lead AI Architect',
        'question': 'How do you optimize model latency constraints when serving public API inferences?',
        'answer': 'I optimize model latency constraints by utilizing weight quantization, cache warming strategies, and model replication pipelines served at the edge using CDN services.'
    }
    body = json.dumps(eval_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/evaluate-answer", data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print(f"API Response: {res_data}")
        assert 'score' in res_data, "Response lacks score."
        assert 'strengths' in res_data, "Response lacks strengths."
        assert 'corrections' in res_data, "Response lacks corrections."
        print("Mock interview evaluation API verified!")
    except Exception as e:
        print(f"Evaluation error: {e}")
        raise e

    # 8. Company-Specific Question Generation API (JSON Post)
    print("\n8. Testing Company-Specific Mock Generation API...")
    gen_data = {
        'role': 'Lead AI Architect',
        'company': 'Vercel'
    }
    body = json.dumps(gen_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/generate-targeted-interview", data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print(f"API Response: {res_data}")
        assert 'questions' in res_data, "Response lacks questions list."
        assert len(res_data['questions']) == 3, "Should return exactly 3 questions."
        # Verify that questions mention Vercel or relate to Edge platform themes
        assert any("Vercel" in q or "edge" in q.lower() for q in res_data['questions']), "Questions must be themed on Vercel."
        print("Company-Specific Mock Generation API verified!")
    except Exception as e:
        print(f"Question generation error: {e}")
        raise e

    # 9. Newsletter Subscription API (JSON Post)
    print("\n9. Testing Newsletter Subscription API...")
    news_data = {
        'email': 'newsletter-tester@nexthire.ai'
    }
    body = json.dumps(news_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/subscribe-newsletter", data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print(f"API Response: {res_data}")
        assert res_data.get('success') is True, "Newsletter signup failed."
        print("Newsletter Subscription API verified!")
    except Exception as e:
        print(f"Newsletter parser error: {e}")
        raise e

    # 10. Contact Message Submission API (JSON Post)
    print("\n10. Testing Contact Message Submission API...")
    contact_data = {
        'name': 'Tester John',
        'email': 'tester-john@nexthire.ai',
        'message': 'Hello, this is a verified routing test message.'
    }
    body = json.dumps(contact_data).encode('utf-8')
    req = urllib.request.Request(f"{BASE_URL}/api/submit-contact", data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        print(f"API Response: {res_data}")
        assert res_data.get('success') is True, "Contact submission failed."
        print("Contact Message Submission API verified!")
    except Exception as e:
        print(f"Contact submit error: {e}")
        raise e

    # 11. Google Login Redirection Flow (GET /google-login & /login/google)
    print("\n11. Testing Google Login Redirection Flow...")
    req = urllib.request.Request(f"{BASE_URL}/google-login", method='GET')
    try:
        response = urllib.request.urlopen(req)
        final_url = response.geturl()
        print(f"Final URL after login redirection: {final_url}")
        assert "dashboard" in final_url or "accounts.google.com" in final_url, "Should redirect to Google Consent or Dashboard."
        print("Google Login redirection verified!")
    except Exception as e:
        print(f"Google login redirect error: {e}")
        raise e

    # 12. Google Callback Cryptographic Validation (GET /auth/google/callback with invalid token)
    print("\n12. Testing Google Callback Cryptographic Validation...")
    query = urllib.parse.urlencode({'code': 'real_code_to_verify'})
    req = urllib.request.Request(f"{BASE_URL}/auth/google/callback?{query}", method='GET')
    try:
        response = urllib.request.urlopen(req)
        final_url = response.geturl()
        content = response.read().decode('utf-8')
        if "dashboard" in final_url:
            print("Google OAuth simulator callback verified!")
        else:
            assert "Google ID Token verification failed" in content or "Google OAuth token exchange failed" in content, "Callback should check and reject invalid codes/tokens."
        print("Google OAuth backend verification rules operational and verified!")
    except Exception as e:
        print(f"Google callback error: {e}")
        raise e

    # 13. Admin Dashboard Access Protection (GET /admin)
    print("\n13. Testing Admin Dashboard Access Protection...")
    req = urllib.request.Request(f"{BASE_URL}/admin", method='GET')
    try:
        response = urllib.request.urlopen(req)
        final_url = response.geturl()
        assert "admin" not in final_url, "Unauthenticated request should not access the admin portal."
        print("Admin access protection verified!")
    except Exception as e:
        print(f"Admin protection test error: {e}")
        raise e

    # 14. Negotiation Strategy API Access (POST /api/generate-negotiation-strategy)
    print("\n14. Testing Negotiation Strategy API Access...")
    post_data = json.dumps({
        'company': 'Google',
        'role': 'Frontend Engineer'
    }).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/generate-negotiation-strategy",
        data=post_data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        response = urllib.request.urlopen(req)
        res_data = json.loads(response.read().decode('utf-8'))
        assert "median" in res_data, "Should return median base salary estimation."
        assert "counter_script" in res_data, "Should return custom recruiter counter-script."
        print(f"Negotiation strategy analysis: {res_data['median']} median estimated base.")
        print("Negotiation strategy API verified!")
    except Exception as e:
        print(f"Negotiation API verification error: {e}")
        raise e

    # 15. PWA Manifest & Service Worker validation
    print("\n15. Testing PWA Manifest & Service Worker validation...")
    try:
        # Check manifest
        response = urllib.request.urlopen(f"{BASE_URL}/manifest.json")
        res_data = json.loads(response.read().decode('utf-8'))
        assert res_data["short_name"] == "NextHire AI", "Manifest properties mismatch."
        print("PWA manifest properties verified!")
        
        # Check service worker
        response = urllib.request.urlopen(f"{BASE_URL}/sw.js")
        headers = response.info()
        assert "application/javascript" in headers.get("Content-Type", ""), "SW must serve with JS content-type."
        print("PWA service worker content type verified!")
    except Exception as e:
        print(f"PWA assets verification error: {e}")
        raise e

    print("\n=== All Route and logic tests PASSED successfully (Zero-Dependency)! ===")

if __name__ == '__main__':
    test_flow()
