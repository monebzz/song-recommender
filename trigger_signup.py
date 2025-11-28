import requests
import uuid

def trigger_signup():
    session = requests.Session()
    base_url = 'http://127.0.0.1:8000'
    
    # Get signup page to get CSRF token
    print("Fetching signup page...")
    try:
        response = session.get(f'{base_url}/signup/')
        if response.status_code != 200:
            print(f"Failed to fetch signup page: {response.status_code}")
            return

        if 'csrftoken' in session.cookies:
            csrftoken = session.cookies['csrftoken']
            print(f"Got CSRF token: {csrftoken}")
        else:
            print("Could not find CSRF token in cookies")
            return
        
        # Generate random user
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        password = "TestPassword123!"
        
        data = {
            'username': username,
            'email': email,
            'password1': password,
            'password2': password,
            'csrfmiddlewaretoken': csrftoken
        }
        
        headers = {
            'Referer': f'{base_url}/signup/'
        }
        
        print(f"Attempting signup for {username}...")
        response = session.post(f'{base_url}/signup/', data=data, headers=headers)
        
        print(f"Signup response status: {response.status_code}")
        
        # If we see the success message or redirect, we know what happened
        if "Account created" in response.text:
            print("Response contains 'Account created'")
        if "failed to send verification email" in response.text:
            print("Response contains 'failed to send verification email'")
            
    except Exception as e:
        print(f"Error triggering signup: {e}")

if __name__ == "__main__":
    trigger_signup()
