#!/usr/bin/env python3
"""
Main entry point for GStrummer application.
This script ensures proper path setup and graceful error handling.
"""

import sys
import os

# Add app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []
    
    try:
        import PySide6
    except ImportError:
        missing.append("PySide6")
    
    try:
        import yaml
    except ImportError:
        missing.append("PyYAML")
        
    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install dependencies with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main application entry point."""
    print("🎸 GStrummer - Guitar Rhythm Trainer")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Import and run the main application
    try:
        from main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"Error importing application: {e}")
        return 1
    except Exception as e:
        print(f"Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())