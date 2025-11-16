"""
Diagnostic script to check Google credentials and API access
Run this to diagnose authentication issues
"""

import os
from dotenv import load_dotenv

load_dotenv()

def check_environment():
    """Check environment variables"""
    print("=" * 60)
    print("Checking Environment Variables")
    print("=" * 60)
    
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    tavily_key = os.getenv("TAVILY_API_KEY")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {'✅ Set' if google_creds else '❌ Not set'}")
    if google_creds:
        print(f"  Value: {google_creds}")
    
    print(f"GOOGLE_API_KEY: {'✅ Set' if google_api_key else '❌ Not set (optional)'}")
    if google_api_key:
        print(f"  Value: {google_api_key[:20]}...")
    
    print(f"TAVILY_API_KEY: {'✅ Set' if tavily_key else '❌ Not set'}")
    if tavily_key:
        print(f"  Value: {tavily_key[:20]}...")
    
    return google_creds, google_api_key, tavily_key

def check_service_account_file():
    """Check if service account file exists"""
    print("\n" + "=" * 60)
    print("Checking Service Account File")
    print("=" * 60)
    
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not google_creds:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        return False
    
    path_dir = os.getcwd()
    service_account_path = os.path.join(path_dir, 'src', google_creds)
    
    if os.path.exists(service_account_path):
        print(f"✅ Service account file found: {service_account_path}")
        
        # Try to read and validate JSON
        try:
            import json
            with open(service_account_path, 'r') as f:
                creds_data = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [field for field in required_fields if field not in creds_data]
            
            if missing:
                print(f"❌ Missing required fields: {missing}")
                return False
            
            print(f"✅ Valid JSON structure")
            print(f"   Project ID: {creds_data.get('project_id')}")
            print(f"   Client Email: {creds_data.get('client_email')}")
            return True
        except json.JSONDecodeError:
            print("❌ Invalid JSON in service account file")
            return False
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
            return False
    else:
        print(f"❌ Service account file not found: {service_account_path}")
        return False

def test_google_auth():
    """Test Google authentication"""
    print("\n" + "=" * 60)
    print("Testing Google Authentication")
    print("=" * 60)
    
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import Request
        
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not google_creds:
            print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
            return False
        
        path_dir = os.getcwd()
        service_account_path = os.path.join(path_dir, 'src', google_creds)
        
        print(f"Loading credentials from: {service_account_path}")
        creds = service_account.Credentials.from_service_account_file(
            service_account_path,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        
        print("Refreshing credentials...")
        creds.refresh(Request())
        
        print("✅ Credentials loaded and refreshed successfully")
        print(f"   Token expires: {creds.expiry}")
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        return False

def test_gemini_api():
    """Test Gemini API access"""
    print("\n" + "=" * 60)
    print("Testing Gemini API Access")
    print("=" * 60)
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.messages import HumanMessage
        
        google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Try with service account first
        if google_creds:
            try:
                from google.oauth2 import service_account
                from google.auth.transport.requests import Request
                
                path_dir = os.getcwd()
                service_account_path = os.path.join(path_dir, 'src', google_creds)
                
                creds = service_account.Credentials.from_service_account_file(
                    service_account_path,
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                creds.refresh(Request())
                
                print("Testing with service account credentials...")
                model = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.7,
                    credentials=creds,
                )
                
                response = model.invoke([HumanMessage(content="Say hello")])
                print(f"✅ Service account authentication works!")
                print(f"   Response: {response.content[:100]}...")
                return True
            except Exception as e:
                print(f"❌ Service account authentication failed: {str(e)}")
                print("   This might mean:")
                print("   1. Gemini API is not enabled for this project")
                print("   2. Service account doesn't have proper permissions")
                print("   3. Try using GOOGLE_API_KEY instead")
        
        # Try with API key
        if google_api_key:
            try:
                print("\nTesting with API key...")
                model = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    temperature=0.7,
                    google_api_key=google_api_key,
                )
                
                response = model.invoke([HumanMessage(content="Say hello")])
                print(f"✅ API key authentication works!")
                print(f"   Response: {response.content[:100]}...")
                return True
            except Exception as e:
                print(f"❌ API key authentication failed: {str(e)}")
        
        print("❌ No working authentication method found")
        return False
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("   Install: pip install langchain-google-genai")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all diagnostic checks"""
    print("\n" + "=" * 60)
    print("Google Credentials Diagnostic Tool")
    print("=" * 60)
    
    google_creds, google_api_key, tavily_key = check_environment()
    
    if google_creds:
        check_service_account_file()
        test_google_auth()
    
    test_gemini_api()
    
    print("\n" + "=" * 60)
    print("Recommendations")
    print("=" * 60)
    
    if not google_creds and not google_api_key:
        print("❌ No Google authentication method configured")
        print("\nOptions:")
        print("1. Use API Key (Recommended for testing):")
        print("   - Get API key from: https://makersuite.google.com/app/apikey")
        print("   - Add to .env: GOOGLE_API_KEY=your_api_key")
        print("\n2. Use Service Account:")
        print("   - Enable Gemini API in Google Cloud Console")
        print("   - Grant service account 'Vertex AI User' role")
        print("   - Add to .env: GOOGLE_APPLICATION_CREDENTIALS=service-account.json")
    
    if google_creds and not test_gemini_api():
        print("\n⚠️  Service account authentication failed. Try using API key instead:")
        print("   GOOGLE_API_KEY=your_api_key")

if __name__ == "__main__":
    main()

