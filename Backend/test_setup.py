#!/usr/bin/env python3
"""
Test script to verify BINDASS GRAND Backend setup
Run this to check if all components are working correctly
"""

import asyncio
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

async def test_database_connection():
    """Test MongoDB connection"""
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

async def test_database_setup():
    """Test database setup and collections"""
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.database_name]
        
        # List collections
        collections = await db.list_collection_names()
        print(f"✅ Database '{settings.database_name}' accessible")
        print(f"📁 Collections: {collections}")
        
        # Test creating a test document
        test_collection = db.test_connection
        await test_collection.insert_one({"test": "connection", "timestamp": "now"})
        await test_collection.delete_many({"test": "connection"})
        print("✅ Database write/read operations successful")
        
        return True
    except Exception as e:
        print(f"❌ Database setup test failed: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def test_imports():
    """Test if all modules can be imported"""
    try:
        from main import app
        from models import User, Contest, PurchasedSeat
        from auth import create_access_token, verify_password
        from database import connect_to_mongo
        from lottery_logic import conduct_lottery_draw
        print("✅ All modules imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 BINDASS GRAND Backend Setup Test")
    print("=" * 50)
    
    # Test imports
    print("\n1. Testing imports...")
    import_success = test_imports()
    
    # Test database connection
    print("\n2. Testing database connection...")
    db_connection_success = await test_database_connection()
    
    # Test database setup
    print("\n3. Testing database setup...")
    db_setup_success = await test_database_setup()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"   DB Connection: {'✅ PASS' if db_connection_success else '❌ FAIL'}")
    print(f"   DB Setup: {'✅ PASS' if db_setup_success else '❌ FAIL'}")
    
    if all([import_success, db_connection_success, db_setup_success]):
        print("\n🎉 All tests passed! Backend is ready to run.")
        print("\nTo start the server, run:")
        print("   python main.py")
        print("   or")
        print("   python run.py")
        print("\nThen visit http://localhost:8000/docs for API documentation")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
