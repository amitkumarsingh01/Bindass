#!/usr/bin/env python3
"""
Quick test to verify BINDASS GRAND Backend is working
"""

def test_imports():
    """Test if all modules can be imported"""
    try:
        print("Testing imports...")
        from main import app
        from models import User, Contest, PurchasedSeat
        from auth import create_access_token, verify_password
        from database import connect_to_mongo
        from lottery_logic import conduct_lottery_draw
        print("✅ All imports successful!")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_app_creation():
    """Test if FastAPI app can be created"""
    try:
        print("Testing FastAPI app creation...")
        from main import app
        print(f"✅ FastAPI app created successfully!")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def main():
    print("🚀 BINDASS GRAND Backend Quick Test")
    print("=" * 50)
    
    # Test imports
    import_success = test_imports()
    
    # Test app creation
    app_success = test_app_creation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   App Creation: {'✅ PASS' if app_success else '❌ FAIL'}")
    
    if import_success and app_success:
        print("\n🎉 Backend is ready to run!")
        print("\nTo start the server:")
        print("   python run.py")
        print("\nThen visit:")
        print("   http://localhost:8000/docs - API Documentation")
        print("   http://localhost:8000/health - Health Check")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
