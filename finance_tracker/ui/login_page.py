import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from db.connection import db
from ui.dashboard import DashboardWindow
from utils.helpers import validate_username, validate_password, show_error, show_success

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Finance Tracker - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create UI elements
        self.create_widgets()
        
        # Current user ID (set after successful login)
        self.current_user_id = None
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create login form widgets"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Personal Finance Tracker", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Login frame
        login_frame = ttk.LabelFrame(self.main_frame, text="Login", padding="10")
        login_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Username
        ttk.Label(login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(login_frame, width=25)
        self.username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(login_frame, width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Login button
        login_btn = ttk.Button(login_frame, text="Login", command=self.login)
        login_btn.grid(row=2, column=1, pady=10, sticky=tk.E)
        
        # Register frame
        register_frame = ttk.LabelFrame(self.main_frame, text="Register", padding="10")
        register_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Register username
        ttk.Label(register_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.reg_username_entry = ttk.Entry(register_frame, width=25)
        self.reg_username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # Register password
        ttk.Label(register_frame, text="Password:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.reg_password_entry = ttk.Entry(register_frame, width=25, show="*")
        self.reg_password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # Confirm password
        ttk.Label(register_frame, text="Confirm:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.reg_confirm_entry = ttk.Entry(register_frame, width=25, show="*")
        self.reg_confirm_entry.grid(row=2, column=1, pady=5, padx=(10, 0))
        
        # Register button
        register_btn = ttk.Button(register_frame, text="Register", command=self.register)
        register_btn.grid(row=3, column=1, pady=10, sticky=tk.E)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
        # Focus on username entry
        self.username_entry.focus()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        # Validate inputs
        if not username:
            show_error("Please enter username")
            return
        
        if not password:
            show_error("Please enter password")
            return
        
        if not validate_username(username):
            show_error("Invalid username format")
            return
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Check credentials in database
        query = "SELECT user_id FROM user WHERE username = %s AND password = %s"
        result = db.execute_query(query, (username, hashed_password))
        
        if result and len(result) > 0:
            self.current_user_id = result[0][0]
            show_success("Login successful!")
            self.open_dashboard()
        else:
            show_error("Invalid username or password")
    
    def register(self):
        """Handle user registration"""
        username = self.reg_username_entry.get().strip()
        password = self.reg_password_entry.get()
        confirm_password = self.reg_confirm_entry.get()
        
        # Validate inputs
        if not username:
            show_error("Please enter username")
            return
        
        if not password:
            show_error("Please enter password")
            return
        
        if not validate_username(username):
            show_error("Username must be at least 3 characters and contain only letters, numbers, and underscores")
            return
        
        if not validate_password(password):
            show_error("Password must be at least 6 characters")
            return
        
        if password != confirm_password:
            show_error("Passwords do not match")
            return
        
        # Check if username already exists
        check_query = "SELECT user_id FROM user WHERE username = %s"
        existing_user = db.execute_query(check_query, (username,))
        
        if existing_user and len(existing_user) > 0:
            show_error("Username already exists")
            return
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Insert new user
        insert_query = "INSERT INTO user (username, password) VALUES (%s, %s)"
        if db.execute_query(insert_query, (username, hashed_password)):
            show_success("Registration successful! You can now login.")
            # Clear register fields
            self.reg_username_entry.delete(0, tk.END)
            self.reg_password_entry.delete(0, tk.END)
            self.reg_confirm_entry.delete(0, tk.END)
        else:
            show_error("Registration failed. Please try again.")
    
    def open_dashboard(self):
        """Open dashboard window"""
        self.root.withdraw()  # Hide login window
        dashboard = DashboardWindow(self.current_user_id, self.root)
        dashboard.show()
    
    def show(self):
        """Show the login window"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the login window
    login_window = LoginWindow()
    login_window.show()
