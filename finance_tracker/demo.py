#!/usr/bin/env python3
"""
Demo script for Personal Finance Tracker

This script demonstrates the application features by:
1. Creating sample data
2. Showing various functionalities
3. Generating sample reports

Run this after setting up the database to see the application in action.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add the current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.connection import db
from utils.helpers import format_currency

def create_demo_user():
    """Create a demo user account"""
    print("Creating demo user...")
    
    # Check if demo user already exists
    check_query = "SELECT user_id FROM user WHERE username = 'demo_user'"
    result = db.execute_query(check_query)
    
    if result and len(result) > 0:
        print("✓ Demo user already exists")
        return result[0][0]
    
    # Create demo user
    import hashlib
    password_hash = hashlib.sha256("demo123".encode()).hexdigest()
    
    insert_query = "INSERT INTO user (username, password) VALUES (%s, %s)"
    if db.execute_query(insert_query, ("demo_user", password_hash)):
        print("✓ Demo user created (username: demo_user, password: demo123)")
        
        # Get the user ID
        result = db.execute_query(check_query)
        return result[0][0] if result else None
    else:
        print("✗ Failed to create demo user")
        return None

def create_demo_transactions(user_id):
    """Create sample transactions for the demo user"""
    print("Creating demo transactions...")
    
    # Get category IDs
    categories_query = "SELECT category_id, category_name FROM category"
    categories_result = db.execute_query(categories_query)
    categories = {row[1]: row[0] for row in categories_result}
    
    # Sample transactions
    transactions = [
        # Income transactions
        ("Salary", "Income", 5000.00, "Monthly salary"),
        ("Freelance", "Income", 1200.00, "Web development project"),
        ("Investment", "Income", 300.00, "Dividend payment"),
        
        # Expense transactions
        ("Food", "Expense", 450.00, "Grocery shopping"),
        ("Transportation", "Expense", 200.00, "Gas and public transport"),
        ("Entertainment", "Expense", 150.00, "Movie tickets and dinner"),
        ("Healthcare", "Expense", 300.00, "Doctor visit"),
        ("Shopping", "Expense", 250.00, "Clothing and electronics"),
        ("Bills", "Expense", 1200.00, "Rent and utilities"),
        ("Food", "Expense", 180.00, "Restaurant meals"),
        ("Transportation", "Expense", 80.00, "Uber rides"),
        ("Entertainment", "Expense", 75.00, "Streaming subscriptions"),
    ]
    
    # Generate transactions for the last 3 months
    base_date = datetime.now() - timedelta(days=90)
    
    for i, (category_name, transaction_type, amount, description) in enumerate(transactions):
        if category_name in categories:
            # Spread transactions over the last 3 months
            transaction_date = base_date + timedelta(days=random.randint(0, 90))
            
            insert_query = """
                INSERT INTO transaction (user_id, category_id, type, amount, date, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            db.execute_query(insert_query, (
                user_id, 
                categories[category_name], 
                transaction_type, 
                amount, 
                transaction_date.date(), 
                description
            ))
    
    print("✓ Demo transactions created")

def create_demo_budget(user_id):
    """Create a demo budget"""
    print("Creating demo budget...")
    
    current_month = datetime.now().strftime('%Y-%m')
    
    # Check if budget already exists
    check_query = "SELECT budget_id FROM budget WHERE user_id = %s AND month = %s"
    result = db.execute_query(check_query, (user_id, current_month))
    
    if result and len(result) > 0:
        print("✓ Demo budget already exists")
        return
    
    # Create budget
    insert_query = "INSERT INTO budget (user_id, month, limit_amount) VALUES (%s, %s, %s)"
    if db.execute_query(insert_query, (user_id, current_month, 3000.00)):
        print("✓ Demo budget created ($3,000 for current month)")
    else:
        print("✗ Failed to create demo budget")

def show_demo_summary(user_id):
    """Show a summary of the demo data"""
    print("\n" + "=" * 50)
    print("DEMO DATA SUMMARY")
    print("=" * 50)
    
    # Get current month
    current_month = datetime.now().strftime('%Y-%m')
    
    # Total income
    income_query = """
        SELECT COALESCE(SUM(amount), 0) as total_income
        FROM transaction 
        WHERE user_id = %s AND type = 'Income' 
        AND DATE_FORMAT(date, '%%Y-%%m') = %s
    """
    income_result = db.execute_query(income_query, (user_id, current_month))
    total_income = income_result[0][0] if income_result else 0
    
    # Total expenses
    expense_query = """
        SELECT COALESCE(SUM(amount), 0) as total_expense
        FROM transaction 
        WHERE user_id = %s AND type = 'Expense' 
        AND DATE_FORMAT(date, '%%Y-%%m') = %s
    """
    expense_result = db.execute_query(expense_query, (user_id, current_month))
    total_expense = expense_result[0][0] if expense_result else 0
    
    # Budget info
    budget_query = "SELECT limit_amount FROM budget WHERE user_id = %s AND month = %s"
    budget_result = db.execute_query(budget_query, (user_id, current_month))
    budget_limit = budget_result[0][0] if budget_result else 0
    
    print(f"Current Month: {current_month}")
    print(f"Total Income: {format_currency(total_income)}")
    print(f"Total Expenses: {format_currency(total_expense)}")
    print(f"Net Savings: {format_currency(total_income - total_expense)}")
    print(f"Budget Limit: {format_currency(budget_limit)}")
    
    if budget_limit > 0:
        budget_usage = (total_expense / budget_limit) * 100
        print(f"Budget Usage: {budget_usage:.1f}%")
        
        if total_expense > budget_limit:
            overspend = total_expense - budget_limit
            print(f"⚠️  OVERSPENDING: {format_currency(overspend)}")
    
    print("\nDemo Login Credentials:")
    print("Username: demo_user")
    print("Password: demo123")
    print("\nYou can now run 'python main.py' and login with these credentials!")

def main():
    """Main demo setup process"""
    print("=" * 60)
    print("Personal Finance Tracker - Demo Setup")
    print("=" * 60)
    
    try:
        # Create demo user
        user_id = create_demo_user()
        if not user_id:
            print("✗ Failed to create demo user")
            return False
        
        # Create demo transactions
        create_demo_transactions(user_id)
        
        # Create demo budget
        create_demo_budget(user_id)
        
        # Show summary
        show_demo_summary(user_id)
        
        print("\n" + "=" * 60)
        print("✓ Demo setup completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"✗ Demo setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
