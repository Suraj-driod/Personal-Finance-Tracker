import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from db.connection import db
from utils.helpers import validate_amount, validate_date, format_currency, show_error, show_success

class AddTransactionWindow:
    def __init__(self, user_id, parent_window=None, callback=None):
        self.user_id = user_id
        self.parent_window = parent_window
        self.callback = callback
        
        # Create window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Add Transaction")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Make window modal
        if parent_window:
            self.root.transient(parent_window)
            self.root.grab_set()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Load categories
        self.load_categories()
        
        # Set default date to today
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Focus on amount entry
        self.amount_entry.focus()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create transaction form widgets"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Add New Transaction", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Form frame
        form_frame = ttk.Frame(self.main_frame)
        form_frame.pack(fill=tk.X, pady=10)
        
        # Transaction Type
        ttk.Label(form_frame, text="Type:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.type_var = tk.StringVar(value="Expense")
        type_frame = ttk.Frame(form_frame)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=5)
        ttk.Radiobutton(type_frame, text="Income", variable=self.type_var, 
                       value="Income", command=self.on_type_change).pack(side=tk.LEFT)
        ttk.Radiobutton(type_frame, text="Expense", variable=self.type_var, 
                       value="Expense", command=self.on_type_change).pack(side=tk.LEFT, padx=(10, 0))
        
        # Category
        ttk.Label(form_frame, text="Category:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                         state="readonly", width=20)
        self.category_combo.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Amount
        ttk.Label(form_frame, text="Amount ($):", font=('Arial', 10, 'bold')).grid(
            row=2, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.amount_entry = ttk.Entry(form_frame, width=25)
        self.amount_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.date_entry = ttk.Entry(form_frame, width=25)
        self.date_entry.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Description
        ttk.Label(form_frame, text="Description:", font=('Arial', 10, 'bold')).grid(
            row=4, column=0, sticky=tk.NW, pady=5, padx=(0, 10))
        self.description_text = tk.Text(form_frame, width=30, height=3)
        self.description_text.grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Save button
        save_btn = ttk.Button(buttons_frame, text="Save Transaction", 
                            command=self.save_transaction)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Cancel button
        cancel_btn = ttk.Button(buttons_frame, text="Cancel", 
                               command=self.cancel)
        cancel_btn.pack(side=tk.LEFT)
        
        # Bind Enter key to save
        self.root.bind('<Return>', lambda e: self.save_transaction())
    
    def load_categories(self):
        """Load categories from database"""
        try:
            query = "SELECT category_name FROM category ORDER BY category_name"
            result = db.execute_query(query)
            
            if result:
                categories = [row[0] for row in result]
                self.category_combo['values'] = categories
                if categories:
                    self.category_combo.set(categories[0])
        except Exception as e:
            show_error(f"Error loading categories: {str(e)}")
    
    def on_type_change(self):
        """Handle transaction type change"""
        # Filter categories based on type
        transaction_type = self.type_var.get()
        
        try:
            if transaction_type == "Income":
                # Show income-related categories
                income_categories = ["Salary", "Freelance", "Investment", "Gift", "Other"]
                self.category_combo['values'] = income_categories
                if income_categories:
                    self.category_combo.set(income_categories[0])
            else:
                # Show all categories (default)
                self.load_categories()
        except Exception as e:
            show_error(f"Error updating categories: {str(e)}")
    
    def save_transaction(self):
        """Save transaction to database"""
        try:
            # Get form data
            transaction_type = self.type_var.get()
            category_name = self.category_var.get()
            amount_str = self.amount_entry.get().strip()
            date_str = self.date_entry.get().strip()
            description = self.description_text.get("1.0", tk.END).strip()
            
            # Validate inputs
            if not category_name:
                show_error("Please select a category")
                return
            
            if not amount_str:
                show_error("Please enter an amount")
                return
            
            # Validate amount
            is_valid_amount, amount = validate_amount(amount_str)
            if not is_valid_amount:
                show_error("Please enter a valid amount")
                return
            
            if not date_str:
                show_error("Please enter a date")
                return
            
            # Validate date
            is_valid_date, transaction_date = validate_date(date_str)
            if not is_valid_date:
                show_error("Please enter a valid date (YYYY-MM-DD)")
                return
            
            # Get category ID
            category_query = "SELECT category_id FROM category WHERE category_name = %s"
            category_result = db.execute_query(category_query, (category_name,))
            
            if not category_result:
                show_error("Invalid category selected")
                return
            
            category_id = category_result[0][0]
            
            # Insert transaction
            insert_query = """
                INSERT INTO transaction (user_id, category_id, type, amount, date, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            if db.execute_query(insert_query, (self.user_id, category_id, transaction_type, 
                                            amount, transaction_date, description)):
                show_success("Transaction saved successfully!")
                
                # Clear form
                self.amount_entry.delete(0, tk.END)
                self.date_entry.delete(0, tk.END)
                self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
                self.description_text.delete("1.0", tk.END)
                
                # Call callback to refresh dashboard
                if self.callback:
                    self.callback()
                
                # Close window after a short delay
                self.root.after(1000, self.cancel)
            else:
                show_error("Failed to save transaction")
                
        except Exception as e:
            show_error(f"Error saving transaction: {str(e)}")
    
    def cancel(self):
        """Cancel and close window"""
        self.root.destroy()
    
    def show(self):
        """Show the window"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the add transaction window
    add_transaction = AddTransactionWindow(1)
    add_transaction.show()
