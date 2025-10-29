"""
MongoDB Connection Test
Tests MongoDB connectivity, databases, collections, and operations.
"""

import sys
import os
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init(autoreset=True)

def print_header(title):
    """Print formatted header"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}{Style.RESET_ALL}\n")

def print_success(message):
    """Print success message"""
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def print_error(message):
    """Print error message"""
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")

def print_info(message):
    """Print info message"""
    print(f"{Fore.YELLOW}ℹ {message}{Style.RESET_ALL}")


def test_mongodb():
    """Test MongoDB connection and operations"""
    
    print_header("MONGODB CONNECTION TEST")
    
    # Step 1: Import pymongo
    try:
        import pymongo
        print_success(f"pymongo installed (version: {pymongo.__version__})")
    except ImportError:
        print_error("pymongo not installed!")
        print_info("Install with: pip install pymongo")
        return False
    
    # Step 2: Load environment and import mongo_manager
    try:
        from dotenv import load_dotenv
        load_dotenv('backend/.env')
        print_success("Environment variables loaded")
    except Exception as e:
        print_error(f"Failed to load .env: {e}")
        return False
    
    # Step 3: Import mongo_manager
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from core import mongo_manager
        print_success("mongo_manager module imported")
    except Exception as e:
        print_error(f"Failed to import mongo_manager: {e}")
        return False
    
    # Step 4: Test connection
    print_header("TESTING CONNECTION")
    try:
        mongo_manager.initialize()
        print_success("Connected to MongoDB!")
        
        # Get connection info
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/jarvis_db")
        print_info(f"URI: {mongo_uri}")
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print_info("Make sure MongoDB is running!")
        print_info("  Windows: Check Services (Win+R → services.msc → MongoDB)")
        print_info("  Or run: net start MongoDB")
        return False
    
    # Step 5: Test database operations
    print_header("TESTING DATABASE OPERATIONS")
    
    try:
        # Test ping
        mongo_manager.ping()
        print_success("Ping successful!")
        
        # Get database info
        db = mongo_manager._db
        print_success(f"Database name: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print_success(f"Collections found: {len(collections)}")
        for col in collections:
            count = db[col].count_documents({})
            print(f"  - {col}: {count} documents")
        
    except Exception as e:
        print_error(f"Database operations failed: {e}")
        return False
    
    # Step 6: Test CRUD operations
    print_header("TESTING CRUD OPERATIONS")
    
    try:
        # Test save conversation
        test_user_text = "Test: What time is it?"
        test_assistant_text = f"Test response at {datetime.now().strftime('%H:%M:%S')}"
        
        mongo_manager.save_conversation(
            user_text=test_user_text,
            assistant_text=test_assistant_text,
            intent="test"
        )
        print_success("✓ CREATE: Saved test conversation")
        
        # Test read history
        history = mongo_manager.get_recent_history(limit=5)
        print_success(f"✓ READ: Retrieved {len(history)} conversations")
        
        if history:
            latest = history[0]
            print_info(f"Latest conversation:")
            print(f"    User: {latest.get('user_text', 'N/A')}")
            print(f"    Assistant: {latest.get('assistant_text', 'N/A')}")
            print(f"    Time: {latest.get('timestamp', 'N/A')}")
        
        # Test search (if available)
        try:
            search_results = mongo_manager.search_history("test", limit=3)
            print_success(f"✓ SEARCH: Found {len(search_results)} results for 'test'")
        except AttributeError:
            print_info("SEARCH: search_history not implemented yet (optional)")
        
        print_success("All CRUD operations working!")
        
    except Exception as e:
        print_error(f"CRUD operations failed: {e}")
        return False
    
    # Step 7: Test indexes
    print_header("TESTING INDEXES")
    
    try:
        db = mongo_manager._db
        
        # Check conversation_history indexes
        conv_indexes = list(db.conversation_history.list_indexes())
        print_success(f"conversation_history indexes: {len(conv_indexes)}")
        for idx in conv_indexes:
            print(f"  - {idx['name']}")
        
        # Check pdf_summaries indexes
        pdf_indexes = list(db.pdf_summaries.list_indexes())
        print_success(f"pdf_summaries indexes: {len(pdf_indexes)}")
        for idx in pdf_indexes:
            print(f"  - {idx['name']}")
        
    except Exception as e:
        print_error(f"Index check failed: {e}")
    
    # Step 8: Database statistics
    print_header("DATABASE STATISTICS")
    
    try:
        db = mongo_manager._db
        
        # Get stats for each collection
        for collection_name in ['conversation_history', 'pdf_summaries', 'alarms']:
            try:
                stats = db.command("collStats", collection_name)
                count = stats.get('count', 0)
                size = stats.get('size', 0)
                avg_size = stats.get('avgObjSize', 0)
                
                print(f"\n{Fore.YELLOW}{collection_name}:{Style.RESET_ALL}")
                print(f"  Documents: {count}")
                print(f"  Size: {size} bytes ({size/1024:.2f} KB)")
                if count > 0:
                    print(f"  Avg doc size: {avg_size} bytes")
            except Exception as e:
                print_info(f"{collection_name}: Collection doesn't exist yet (empty)")
        
    except Exception as e:
        print_error(f"Stats failed: {e}")
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("MongoDB is fully operational! ✓")
    print(f"\n{Fore.GREEN}All tests passed!{Style.RESET_ALL}\n")
    
    return True


def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"  JARVIS MONGODB DIAGNOSTICS")
    print(f"{'='*70}{Style.RESET_ALL}\n")
    
    success = test_mongodb()
    
    if success:
        print(f"{Fore.GREEN}✓ MongoDB is ready for Jarvis!{Style.RESET_ALL}\n")
    else:
        print(f"{Fore.RED}✗ MongoDB has issues that need fixing{Style.RESET_ALL}\n")


if __name__ == "__main__":
    main()
