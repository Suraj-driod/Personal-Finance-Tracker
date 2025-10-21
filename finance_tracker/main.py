#!/usr/bin/env python3
"""
Personal Finance Tracker - Main Entry Point

A comprehensive personal finance management application built with:
- Python Tkinter for GUI
- MySQL for database
- Matplotlib for analytics charts
- Pandas for data manipulation

Features:
- User authentication (login/register)
- Transaction management (income/expense tracking)
- Budget management with progress tracking
- Financial reports with charts and export
- Category-based expense analysis

Author: Personal Finance Tracker Team
Version: 1.0
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.login_page import LoginWindow
from db.connection import db

def check_database_connection():
    """Check if database connection is available"""
    try:
        connection = db.get_connection()
        if connection:
            print("✓ Database connection successful")
            return True
        else:
            print("✗ Database connection failed")
            return False
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return False

def show_database_setup_instructions():
    """Show instructions for database setup"""
    instructions = """
Database Setup Required:

1. Install MySQL Server on your system
2. Create a database named 'finance_tracker'
3. Update the database credentials in db/connection.py:
   - host: "localhost" (or your MySQL host)
   - user: "root" (or your MySQL username)
   - password: "yourpassword" (your MySQL password)
   - database: "finance_tracker"

4. Run the SQL setup script:
   mysql -u root -p finance_tracker < db/setup.sql

5. Install required Python packages:
   pip install mysql-connector-python matplotlib pandas

After setup, restart the application.
    """
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Database Setup Required", instructions)
    root.destroy()

def main():
    """Main application entry point"""
    print("=" * 50)
    print("Personal Finance Tracker v1.0")
    print("=" * 50)
    
    # Check database connection
    if not check_database_connection():
        show_database_setup_instructions()
        return
    
    try:
        # Create and show login window
        print("Starting Personal Finance Tracker...")
        login_window = LoginWindow()
        login_window.show()
        
    except Exception as e:
        print(f"Application error: {e}")
        messagebox.showerror("Application Error", f"An error occurred: {e}")
    
    finally:
        # Close database connection
        db.close_connection()
        print("Application closed.")

if __name__ == "__main__":
    main()
