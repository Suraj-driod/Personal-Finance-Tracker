import re
from datetime import datetime, date
from typing import Optional, Tuple
import tkinter as tk
from tkinter import messagebox

def validate_amount(amount_str: str) -> Tuple[bool, Optional[float]]:
    """Validate and convert amount string to float"""
    try:
        # Remove any non-numeric characters except decimal point
        cleaned = re.sub(r'[^\d.]', '', amount_str)
        if not cleaned:
            return False, None
        
        amount = float(cleaned)
        if amount < 0:
            return False, None
        
        return True, amount
    except ValueError:
        return False, None

def validate_date(date_str: str) -> Tuple[bool, Optional[date]]:
    """Validate date string and convert to date object"""
    try:
        # Try different date formats
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                return True, datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        
        return False, None
    except:
        return False, None

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date_display(date_obj: date) -> str:
    """Format date for display"""
    return date_obj.strftime('%d/%m/%Y')

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3:
        return False
    
    # Username should contain only alphanumeric characters and underscores
    return bool(re.match(r'^[a-zA-Z0-9_]+$', username))

def validate_password(password: str) -> bool:
    """Validate password format"""
    if not password or len(password) < 6:
        return False
    
    return True

def show_error(message: str, title: str = "Error"):
    """Show error message box"""
    messagebox.showerror(title, message)

def show_success(message: str, title: str = "Success"):
    """Show success message box"""
    messagebox.showinfo(title, message)

def show_warning(message: str, title: str = "Warning"):
    """Show warning message box"""
    messagebox.showwarning(title, message)

def confirm_action(message: str, title: str = "Confirm") -> bool:
    """Show confirmation dialog"""
    return messagebox.askyesno(title, message)

def get_current_month() -> str:
    """Get current month in YYYY-MM format"""
    return datetime.now().strftime('%Y-%m')

def get_month_name(month_str: str) -> str:
    """Convert YYYY-MM to Month Year format"""
    try:
        date_obj = datetime.strptime(month_str, '%Y-%m')
        return date_obj.strftime('%B %Y')
    except:
        return month_str

def calculate_percentage(part: float, total: float) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0
    return (part / total) * 100

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def is_valid_email(email: str) -> bool:
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent SQL injection"""
    # Remove or escape potentially dangerous characters
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    sanitized = text
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized.strip()
