import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
from db.connection import db
from utils.helpers import format_currency, show_error, show_success, format_date_display
from utils.charts import ChartGenerator

class ReportsWindow:
    def __init__(self, user_id, parent_window=None):
        self.user_id = user_id
        self.parent_window = parent_window
        
        # Create window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("Financial Reports")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)
        
        # Center the window
        self.center_window()
        
        # Make window modal
        if parent_window:
            self.root.transient(parent_window)
            self.root.grab_set()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create widgets
        self.create_widgets()
        
        # Load initial data
        self.load_transactions()
        
        # Chart generator
        self.chart_generator = None
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create reports widgets"""
        # Title
        title_label = ttk.Label(self.main_frame, text="Financial Reports", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Filters frame
        filters_frame = ttk.LabelFrame(self.main_frame, text="Filters", padding="10")
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Date range filters
        date_frame = ttk.Frame(filters_frame)
        date_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(date_frame, text="From:").pack(side=tk.LEFT, padx=(0, 5))
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.from_date_entry = ttk.Entry(date_frame, textvariable=self.from_date_var, width=12)
        self.from_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Label(date_frame, text="To:").pack(side=tk.LEFT, padx=(0, 5))
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.to_date_entry = ttk.Entry(date_frame, textvariable=self.to_date_var, width=12)
        self.to_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Transaction type filter
        type_frame = ttk.Frame(filters_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, 
                                 values=["All", "Income", "Expense"], state="readonly", width=10)
        type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Filter button
        filter_btn = ttk.Button(type_frame, text="Apply Filters", command=self.load_transactions)
        filter_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        export_btn = ttk.Button(type_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.pack(side=tk.LEFT)
        
        # Transactions table frame
        table_frame = ttk.LabelFrame(self.main_frame, text="Transactions", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for transactions
        columns = ('Date', 'Type', 'Category', 'Amount', 'Description')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Define column headings and widths
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Description':
                self.tree.column(col, width=200)
            elif col == 'Amount':
                self.tree.column(col, width=100)
            else:
                self.tree.column(col, width=120)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Charts frame
        charts_frame = ttk.LabelFrame(self.main_frame, text="Analytics Charts", padding="10")
        charts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chart buttons
        chart_buttons_frame = ttk.Frame(charts_frame)
        chart_buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(chart_buttons_frame, text="Expense Pie Chart", 
                  command=self.show_expense_pie_chart).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(chart_buttons_frame, text="Income vs Expense", 
                  command=self.show_income_expense_chart).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(chart_buttons_frame, text="Category Bar Chart", 
                  command=self.show_category_bar_chart).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(chart_buttons_frame, text="Clear Charts", 
                  command=self.clear_charts).pack(side=tk.LEFT)
        
        # Chart display area
        self.chart_frame = ttk.Frame(charts_frame)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Close button
        close_btn = ttk.Button(self.main_frame, text="Close", command=self.close_window)
        close_btn.pack(pady=10)
    
    def load_transactions(self):
        """Load transactions based on filters"""
        try:
            # Get filter values
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            transaction_type = self.type_var.get()
            
            # Build query
            query = """
                SELECT t.date, t.type, c.category_name, t.amount, t.description
                FROM transaction t
                JOIN category c ON t.category_id = c.category_id
                WHERE t.user_id = %s
            """
            params = [self.user_id]
            
            # Add date filters
            if from_date:
                query += " AND t.date >= %s"
                params.append(from_date)
            
            if to_date:
                query += " AND t.date <= %s"
                params.append(to_date)
            
            # Add type filter
            if transaction_type != "All":
                query += " AND t.type = %s"
                params.append(transaction_type)
            
            query += " ORDER BY t.date DESC, t.created_at DESC"
            
            # Execute query
            result = db.execute_query(query, tuple(params))
            
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Insert new data
            if result:
                for row in result:
                    date_str = format_date_display(row[0])
                    amount_str = format_currency(row[3])
                    description = row[4] if row[4] else ""
                    
                    # Color code based on type
                    item = self.tree.insert('', 'end', values=(
                        date_str, row[1], row[2], amount_str, description
                    ))
                    
                    # Color code items
                    if row[1] == 'Income':
                        self.tree.set(item, 'Amount', f"+{amount_str}")
                    else:
                        self.tree.set(item, 'Amount', f"-{amount_str}")
            
            show_success(f"Loaded {len(result) if result else 0} transactions")
            
        except Exception as e:
            show_error(f"Error loading transactions: {str(e)}")
    
    def export_to_csv(self):
        """Export transactions to CSV file"""
        try:
            # Get current data from treeview
            data = []
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                data.append(values)
            
            if not data:
                show_error("No data to export")
                return
            
            # Ask for file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save CSV file"
            )
            
            if filename:
                # Create DataFrame and save
                df = pd.DataFrame(data, columns=['Date', 'Type', 'Category', 'Amount', 'Description'])
                df.to_csv(filename, index=False)
                show_success(f"Data exported to {filename}")
            
        except Exception as e:
            show_error(f"Error exporting data: {str(e)}")
    
    def show_expense_pie_chart(self):
        """Show expense pie chart"""
        try:
            # Get expense data for the filtered period
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            query = """
                SELECT c.category_name, SUM(t.amount) as total_amount
                FROM transaction t
                JOIN category c ON t.category_id = c.category_id
                WHERE t.user_id = %s AND t.type = 'Expense'
            """
            params = [self.user_id]
            
            if from_date:
                query += " AND t.date >= %s"
                params.append(from_date)
            
            if to_date:
                query += " AND t.date <= %s"
                params.append(to_date)
            
            query += " GROUP BY c.category_id, c.category_name ORDER BY total_amount DESC"
            
            result = db.execute_query(query, tuple(params))
            
            if result:
                categories = [row[0] for row in result]
                amounts = [float(row[1]) for row in result]
                
                # Create chart generator if not exists
                if not self.chart_generator:
                    self.chart_generator = ChartGenerator(self.chart_frame)
                
                # Create pie chart
                chart_data = dict(zip(categories, amounts))
                fig = self.chart_generator.create_pie_chart(chart_data, "Expense Distribution")
                
                if fig:
                    self.chart_generator.display_chart(fig)
            else:
                show_error("No expense data available for the selected period")
                
        except Exception as e:
            show_error(f"Error creating pie chart: {str(e)}")
    
    def show_income_expense_chart(self):
        """Show income vs expense trend chart"""
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            # Get income data
            income_query = """
                SELECT DATE_FORMAT(date, '%%Y-%%m-01') as month, SUM(amount) as total_amount
                FROM transaction
                WHERE user_id = %s AND type = 'Income'
            """
            income_params = [self.user_id]
            
            if from_date:
                income_query += " AND date >= %s"
                income_params.append(from_date)
            
            if to_date:
                income_query += " AND date <= %s"
                income_params.append(to_date)
            
            income_query += " GROUP BY DATE_FORMAT(date, '%%Y-%%m-01') ORDER BY month"
            
            income_result = db.execute_query(income_query, tuple(income_params))
            
            # Get expense data
            expense_query = """
                SELECT DATE_FORMAT(date, '%%Y-%%m-01') as month, SUM(amount) as total_amount
                FROM transaction
                WHERE user_id = %s AND type = 'Expense'
            """
            expense_params = [self.user_id]
            
            if from_date:
                expense_query += " AND date >= %s"
                expense_params.append(from_date)
            
            if to_date:
                expense_query += " AND date <= %s"
                expense_params.append(to_date)
            
            expense_query += " GROUP BY DATE_FORMAT(date, '%%Y-%%m-01') ORDER BY month"
            
            expense_result = db.execute_query(expense_query, tuple(expense_params))
            
            if income_result or expense_result:
                # Create chart generator if not exists
                if not self.chart_generator:
                    self.chart_generator = ChartGenerator(self.chart_frame)
                
                # Prepare data
                income_data = [(datetime.strptime(row[0], '%Y-%m-%d'), float(row[1])) 
                             for row in income_result] if income_result else []
                expense_data = [(datetime.strptime(row[0], '%Y-%m-%d'), float(row[1])) 
                              for row in expense_result] if expense_result else []
                
                # Create chart
                fig = self.chart_generator.create_income_expense_chart(
                    income_data, expense_data, "Income vs Expense Trend"
                )
                
                if fig:
                    self.chart_generator.display_chart(fig)
            else:
                show_error("No data available for the selected period")
                
        except Exception as e:
            show_error(f"Error creating income vs expense chart: {str(e)}")
    
    def show_category_bar_chart(self):
        """Show category comparison bar chart"""
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            query = """
                SELECT c.category_name, 
                       SUM(CASE WHEN t.type = 'Income' THEN t.amount ELSE 0 END) as income,
                       SUM(CASE WHEN t.type = 'Expense' THEN t.amount ELSE 0 END) as expense
                FROM category c
                LEFT JOIN transaction t ON c.category_id = t.category_id 
                    AND t.user_id = %s
            """
            params = [self.user_id]
            
            if from_date:
                query += " AND t.date >= %s"
                params.append(from_date)
            
            if to_date:
                query += " AND t.date <= %s"
                params.append(to_date)
            
            query += """
                GROUP BY c.category_id, c.category_name
                HAVING income > 0 OR expense > 0
                ORDER BY (income + expense) DESC
            """
            
            result = db.execute_query(query, tuple(params))
            
            if result:
                # Create chart generator if not exists
                if not self.chart_generator:
                    self.chart_generator = ChartGenerator(self.chart_frame)
                
                # Prepare data for bar chart (using total amounts)
                categories = [row[0] for row in result]
                amounts = [float(row[1]) + float(row[2]) for row in result]  # income + expense
                
                chart_data = dict(zip(categories, amounts))
                fig = self.chart_generator.create_bar_chart(chart_data, "Category Comparison")
                
                if fig:
                    self.chart_generator.display_chart(fig)
            else:
                show_error("No data available for the selected period")
                
        except Exception as e:
            show_error(f"Error creating bar chart: {str(e)}")
    
    def clear_charts(self):
        """Clear all charts"""
        if self.chart_generator:
            self.chart_generator.clear_chart()
    
    def close_window(self):
        """Close the window"""
        self.root.destroy()
    
    def show(self):
        """Show the window"""
        self.root.mainloop()

if __name__ == "__main__":
    # Test the reports window
    reports_window = ReportsWindow(1)
    reports_window.show()
