import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db.connection import db
from utils.helpers import format_currency, get_current_month, show_error, show_success, get_month_name

class BudgetWindow:
    def __init__(self, user_id, parent_window=None, callback=None):
        self.user_id = user_id
        self.parent_window = parent_window
        self.callback = callback
        
        # Create window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Budget Management")
        self.root.geometry("600x500")
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
        
        # Load current budget data
        self.load_budget_data()
        
        # Focus on limit entry
        self.limit_entry.focus()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create budget management widgets"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Budget Management", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Current month info
        current_month = get_current_month()
        month_name = get_month_name(current_month)
        
        month_label = ttk.Label(self.main_frame, text=f"Managing Budget for: {month_name}", 
                               font=('Arial', 12, 'bold'))
        month_label.pack(pady=(0, 10))
        
        # Budget setting frame
        budget_frame = ttk.LabelFrame(self.main_frame, text="Set Monthly Budget", padding="15")
        budget_frame.pack(fill=tk.X, pady=10)
        
        # Budget limit
        ttk.Label(budget_frame, text="Budget Limit ($):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=5, padx=(0, 10))
        self.limit_entry = ttk.Entry(budget_frame, width=20)
        self.limit_entry.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Set budget button
        set_budget_btn = ttk.Button(budget_frame, text="Set Budget", 
                                   command=self.set_budget)
        set_budget_btn.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # Current budget display frame
        self.budget_display_frame = ttk.LabelFrame(self.main_frame, text="Current Budget Status", padding="15")
        self.budget_display_frame.pack(fill=tk.X, pady=10)
        
        # Create budget status labels
        self.create_budget_status_labels()
        
        # Progress bar frame
        progress_frame = ttk.Frame(self.budget_display_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(progress_frame, text="Budget Usage:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100, length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Progress percentage label
        self.progress_label = ttk.Label(progress_frame, text="0%", font=('Arial', 10))
        self.progress_label.pack(anchor=tk.W)
        
        # Overspending alert
        self.alert_label = ttk.Label(self.budget_display_frame, text="", 
                                    font=('Arial', 10, 'bold'), foreground='red')
        self.alert_label.pack(pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)
        
        # Refresh button
        refresh_btn = ttk.Button(buttons_frame, text="Refresh", 
                               command=self.load_budget_data)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(buttons_frame, text="Close", 
                              command=self.close_window)
        close_btn.pack(side=tk.LEFT)
        
        # Bind Enter key to set budget
        self.root.bind('<Return>', lambda e: self.set_budget())
    
    def create_budget_status_labels(self):
        """Create labels for budget status display"""
        # Budget limit label
        ttk.Label(self.budget_display_frame, text="Budget Limit:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.budget_limit_label = ttk.Label(self.budget_display_frame, text="$0.00", 
                                           font=('Arial', 10))
        self.budget_limit_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Current spending label
        ttk.Label(self.budget_display_frame, text="Current Spending:", 
                 font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.spending_label = ttk.Label(self.budget_display_frame, text="$0.00", 
                                       font=('Arial', 10))
        self.spending_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Remaining budget label
        ttk.Label(self.budget_display_frame, text="Remaining:", 
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.remaining_label = ttk.Label(self.budget_display_frame, text="$0.00", 
                                        font=('Arial', 10))
        self.remaining_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
    
    def load_budget_data(self):
        """Load current budget data"""
        try:
            current_month = get_current_month()
            
            # Get current budget limit
            budget_query = """
                SELECT limit_amount FROM budget 
                WHERE user_id = %s AND month = %s
            """
            budget_result = db.execute_query(budget_query, (self.user_id, current_month))
            
            budget_limit = 0
            if budget_result and len(budget_result) > 0:
                budget_limit = float(budget_result[0][0])
                self.limit_entry.delete(0, tk.END)
                self.limit_entry.insert(0, str(budget_limit))
            
            # Get current month expenses
            expense_query = """
                SELECT COALESCE(SUM(amount), 0) as total_expense
                FROM transaction 
                WHERE user_id = %s AND type = 'Expense' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            expense_result = db.execute_query(expense_query, (self.user_id, current_month))
            current_spending = float(expense_result[0][0]) if expense_result else 0
            
            # Update labels
            self.budget_limit_label.config(text=format_currency(budget_limit))
            self.spending_label.config(text=format_currency(current_spending))
            
            # Calculate remaining budget
            remaining = budget_limit - current_spending
            self.remaining_label.config(text=format_currency(remaining))
            
            # Update progress bar
            if budget_limit > 0:
                progress_percentage = (current_spending / budget_limit) * 100
                self.progress_var.set(min(progress_percentage, 100))
                self.progress_label.config(text=f"{progress_percentage:.1f}%")
                
                # Show overspending alert
                if current_spending > budget_limit:
                    overspend_amount = current_spending - budget_limit
                    self.alert_label.config(
                        text=f"⚠️ OVERSpending Alert! You have exceeded your budget by {format_currency(overspend_amount)}"
                    )
                    self.progress_bar.config(style='danger.Horizontal.TProgressbar')
                else:
                    self.alert_label.config(text="")
                    self.progress_bar.config(style='default')
            else:
                self.progress_var.set(0)
                self.progress_label.config(text="0%")
                self.alert_label.config(text="No budget set for this month")
            
        except Exception as e:
            show_error(f"Error loading budget data: {str(e)}")
    
    def set_budget(self):
        """Set monthly budget"""
        try:
            limit_str = self.limit_entry.get().strip()
            
            if not limit_str:
                show_error("Please enter a budget limit")
                return
            
            # Validate amount
            try:
                limit_amount = float(limit_str)
                if limit_amount < 0:
                    show_error("Budget limit must be positive")
                    return
            except ValueError:
                show_error("Please enter a valid amount")
                return
            
            current_month = get_current_month()
            
            # Check if budget already exists
            check_query = """
                SELECT budget_id FROM budget 
                WHERE user_id = %s AND month = %s
            """
            existing_budget = db.execute_query(check_query, (self.user_id, current_month))
            
            if existing_budget and len(existing_budget) > 0:
                # Update existing budget
                update_query = """
                    UPDATE budget SET limit_amount = %s 
                    WHERE user_id = %s AND month = %s
                """
                if db.execute_query(update_query, (limit_amount, self.user_id, current_month)):
                    show_success("Budget updated successfully!")
                else:
                    show_error("Failed to update budget")
            else:
                # Insert new budget
                insert_query = """
                    INSERT INTO budget (user_id, month, limit_amount)
                    VALUES (%s, %s, %s)
                """
                if db.execute_query(insert_query, (self.user_id, current_month, limit_amount)):
                    show_success("Budget set successfully!")
                else:
                    show_error("Failed to set budget")
            
            # Refresh data
            self.load_budget_data()
            
            # Call callback to refresh dashboard
            if self.callback:
                self.callback()
                
        except Exception as e:
            show_error(f"Error setting budget: {str(e)}")
    
    def close_window(self):
        """Close the window"""
        self.root.destroy()
    
    def show(self):
        """Show the window"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the budget window
    budget_window = BudgetWindow(1)
    budget_window.show()
