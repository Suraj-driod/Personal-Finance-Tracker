import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from db.connection import db
from utils.helpers import format_currency, get_current_month, show_error
from utils.charts import ChartGenerator
from ui.add_transaction import AddTransactionWindow
from ui.budget_page import BudgetWindow
from ui.reports_page import ReportsWindow

class DashboardWindow:
    def __init__(self, user_id, parent_window=None):
        self.user_id = user_id
        self.parent_window = parent_window
        
        # Create main window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Personal Finance Tracker - Dashboard")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Create main frame with scrollbar
        self.create_main_frame()
        
        # Create UI elements
        self.create_widgets()
        
        # Load dashboard data
        self.load_dashboard_data()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_main_frame(self):
        """Create main frame with scrollbar"""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_widgets(self):
        """Create dashboard widgets"""
        # Header frame
        header_frame = ttk.Frame(self.scrollable_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(header_frame, text="Personal Finance Dashboard", 
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Logout button
        logout_btn = ttk.Button(header_frame, text="Logout", command=self.logout)
        logout_btn.pack(side=tk.RIGHT)
        
        # Summary frame
        self.summary_frame = ttk.LabelFrame(self.scrollable_frame, text="Financial Summary", padding="10")
        self.summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Create summary labels
        self.create_summary_labels()
        
        # Charts frame
        self.charts_frame = ttk.LabelFrame(self.scrollable_frame, text="Analytics", padding="10")
        self.charts_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create chart generator
        self.chart_generator = ChartGenerator(self.charts_frame)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.scrollable_frame)
        buttons_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Action buttons
        ttk.Button(buttons_frame, text="Add Transaction", 
                  command=self.open_add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Manage Budget", 
                  command=self.open_budget).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="View Reports", 
                  command=self.open_reports).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Refresh", 
                  command=self.load_dashboard_data).pack(side=tk.LEFT, padx=5)
    
    def create_summary_labels(self):
        """Create summary labels for financial overview"""
        # Create grid layout for summary
        summary_grid = ttk.Frame(self.summary_frame)
        summary_grid.pack(fill=tk.X)
        
        # Total Income
        ttk.Label(summary_grid, text="Total Income:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.income_label = ttk.Label(summary_grid, text="$0.00", 
                                     font=('Arial', 12), foreground='green')
        self.income_label.grid(row=0, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Total Expenses
        ttk.Label(summary_grid, text="Total Expenses:", font=('Arial', 12, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.expense_label = ttk.Label(summary_grid, text="$0.00", 
                                      font=('Arial', 12), foreground='red')
        self.expense_label.grid(row=1, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Net Savings
        ttk.Label(summary_grid, text="Net Savings:", font=('Arial', 12, 'bold')).grid(
            row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.savings_label = ttk.Label(summary_grid, text="$0.00", 
                                      font=('Arial', 12), foreground='blue')
        self.savings_label.grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Current Month
        ttk.Label(summary_grid, text="Current Month:", font=('Arial', 12, 'bold')).grid(
            row=0, column=2, sticky=tk.W, padx=10, pady=5)
        self.month_label = ttk.Label(summary_grid, text=get_current_month(), 
                                    font=('Arial', 12))
        self.month_label.grid(row=0, column=3, sticky=tk.W, padx=10, pady=5)
    
    def load_dashboard_data(self):
        """Load and display dashboard data"""
        try:
            # Get current month
            current_month = get_current_month()
            
            # Get total income for current month
            income_query = """
                SELECT COALESCE(SUM(amount), 0) as total_income
                FROM transaction 
                WHERE user_id = %s AND type = 'Income' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            income_result = db.execute_query(income_query, (self.user_id, current_month))
            total_income = income_result[0][0] if income_result else 0
            
            # Get total expenses for current month
            expense_query = """
                SELECT COALESCE(SUM(amount), 0) as total_expense
                FROM transaction 
                WHERE user_id = %s AND type = 'Expense' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            expense_result = db.execute_query(expense_query, (self.user_id, current_month))
            total_expense = expense_result[0][0] if expense_result else 0
            
            # Calculate savings
            net_savings = total_income - total_expense
            
            # Update labels
            self.income_label.config(text=format_currency(total_income))
            self.expense_label.config(text=format_currency(total_expense))
            self.savings_label.config(text=format_currency(net_savings))
            
            # Update savings color based on value
            if net_savings >= 0:
                self.savings_label.config(foreground='green')
            else:
                self.savings_label.config(foreground='red')
            
            # Load expense category chart
            self.load_expense_chart()
            
        except Exception as e:
            show_error(f"Error loading dashboard data: {str(e)}")
    
    def load_expense_chart(self):
        """Load expense category pie chart"""
        try:
            # Get expense data by category for current month
            current_month = get_current_month()
            chart_query = """
                SELECT c.category_name, COALESCE(SUM(t.amount), 0) as total_amount
                FROM category c
                LEFT JOIN transaction t ON c.category_id = t.category_id 
                    AND t.user_id = %s AND t.type = 'Expense' 
                    AND DATE_FORMAT(t.date, '%%Y-%%m') = %s
                GROUP BY c.category_id, c.category_name
                HAVING total_amount > 0
                ORDER BY total_amount DESC
            """
            
            chart_result = db.execute_query(chart_query, (self.user_id, current_month))
            
            if chart_result:
                # Prepare data for chart
                categories = [row[0] for row in chart_result]
                amounts = [float(row[1]) for row in chart_result]
                
                # Create pie chart
                chart_data = dict(zip(categories, amounts))
                fig = self.chart_generator.create_pie_chart(
                    chart_data, "Expense by Category - Current Month"
                )
                
                if fig:
                    self.chart_generator.display_chart(fig, row=0, column=0)
            else:
                # Show message if no data
                no_data_label = ttk.Label(self.charts_frame, 
                                        text="No expense data available for current month",
                                        font=('Arial', 12))
                no_data_label.grid(row=0, column=0, pady=20)
                
        except Exception as e:
            show_error(f"Error loading chart: {str(e)}")
    
    def open_add_transaction(self):
        """Open add transaction window"""
        AddTransactionWindow(self.user_id, self.root, self.load_dashboard_data)
    
    def open_budget(self):
        """Open budget management window"""
        BudgetWindow(self.user_id, self.root, self.load_dashboard_data)
    
    def open_reports(self):
        """Open reports window"""
        ReportsWindow(self.user_id, self.root)
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            if self.parent_window:
                self.parent_window.deiconify()  # Show login window
    
    def on_closing(self):
        """Handle window closing"""
        if self.parent_window:
            self.parent_window.destroy()  # Close login window too
        self.root.destroy()
    
    def show(self):
        """Show the dashboard window"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the dashboard (requires user_id)
    dashboard = DashboardWindow(1)
    dashboard.show()
