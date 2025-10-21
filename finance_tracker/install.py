#!/usr/bin/env python3
"""
Installation script for Personal Finance Tracker

This script helps set up the application by:
1. Installing required Python packages
2. Checking database connection
3. Setting up the database schema
4. Providing setup instructions

Run this script before using the application for the first time.
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required Python packages"""
    print("Installing Python packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Python packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install packages: {e}")
        return False

def check_mysql_connection():
    """Check if MySQL is available"""
    print("Checking MySQL connection...")
    try:
        import mysql.connector
        from db.connection import db
        
        connection = db.get_connection()
        if connection:
            print("✓ MySQL connection successful")
            return True
        else:
            print("✗ MySQL connection failed")
            return False
    except ImportError:
        print("✗ mysql-connector-python not installed")
        return False
    except Exception as e:
        print(f"✗ MySQL connection error: {e}")
        return False

def setup_database():
    """Setup database schema"""
    print("Setting up database schema...")
    try:
        from db.connection import db
        
        # Read and execute setup.sql
        setup_sql_path = Path("db/setup.sql")
        if setup_sql_path.exists():
            with open(setup_sql_path, 'r') as f:
                sql_script = f.read()
            
            # Split script into individual statements
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    db.execute_query(statement)
            
            print("✓ Database schema created successfully")
            return True
        else:
            print("✗ setup.sql file not found")
            return False
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

def main():
    """Main installation process"""
    print("=" * 60)
    print("Personal Finance Tracker - Installation Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("✗ Please run this script from the finance_tracker directory")
        return False
    
    # Step 1: Install Python packages
    if not install_requirements():
        print("\nPlease install the required packages manually:")
        print("pip install -r requirements.txt")
        return False
    
    # Step 2: Check MySQL connection
    if not check_mysql_connection():
        print("\nMySQL setup required:")
        print("1. Install MySQL Server")
        print("2. Create database 'finance_tracker'")
        print("3. Update credentials in db/connection.py")
        print("4. Run this script again")
        return False
    
    # Step 3: Setup database
    if not setup_database():
        print("\nDatabase setup failed. Please check your MySQL configuration.")
        return False
    
    print("\n" + "=" * 60)
    print("✓ Installation completed successfully!")
    print("=" * 60)
    print("\nYou can now run the application with:")
    print("python main.py")
    print("\nOr on Windows:")
    print("python main.py")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
