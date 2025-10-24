import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
# Assuming these imports are correct and available
from db.connection import db
from utils.helpers import format_currency, get_current_month, show_error
from utils.charts import ChartGenerator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter.font as tkFont

# Base Frame Class
class BaseFrame(tk.Frame):
    def __init__(self, parent, user_id, colors):
        super().__init__(parent, bg=colors['bg_main'])
        self.user_id = user_id
        self.colors = colors
        self.setup_frame()
    
    def setup_frame(self):
        """Override this method in subclasses to create frame content"""
        pass
    
    def refresh_data(self):
        """Override this method in subclasses to refresh frame data"""
        pass

# Dashboard Frame
class DashboardFrame(BaseFrame):
    def setup_frame(self):
        """Create dashboard content"""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Summary Cards
        self.grid_rowconfigure(2, weight=1)  # Charts section
        self.grid_rowconfigure(3, weight=0)  # Recent transactions
        
        # Create sections
        self.create_header()
        self.create_summary_cards()
        self.create_charts_section()
        self.create_recent_transactions()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self, bg=self.colors['bg_main'])
        header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(25, 15))
        
        # Main title
        main_title = tk.Label(header_frame, text="Dashboard", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        main_title.pack(anchor=tk.W, pady=(15, 8))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Overview of your financial activity", 
                            font=('Segoe UI', 15), 
                            bg=self.colors['bg_main'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor=tk.W)
    
    def create_summary_cards(self):
        """Create summary cards for financial overview"""
        cards_frame = tk.Frame(self, bg=self.colors['bg_main'])
        cards_frame.grid(row=1, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        cards_container = tk.Frame(cards_frame, bg=self.colors['bg_main'])
        cards_container.pack(expand=True)
        
        self.income_card = self.create_summary_card(cards_container, "Total Income", "$0.00", 
                                                    "+0% from last month", self.colors['accent_green'], "📈")
        self.income_card.pack(side=tk.LEFT, padx=(0, 15))
        
        self.expense_card = self.create_summary_card(cards_container, "Total Expenses", "$0.00", 
                                                     "+0% from last month", self.colors['accent_red'], "📉")
        self.expense_card.pack(side=tk.LEFT, padx=(0, 15))
        
        self.balance_card = self.create_summary_card(cards_container, "Balance", "$0.00", 
                                                     "Available balance", self.colors['accent_blue'], "💰")
        self.balance_card.pack(side=tk.LEFT)
    
    def create_summary_card(self, parent, title, amount, change, color, icon):
        """Create a summary card"""
        card = tk.Frame(parent, bg=self.colors['bg_cards'], relief='groove', bd=1)
        card.configure(width=220, height=140)
        
        content_frame = tk.Frame(card, bg=self.colors['bg_cards'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Icon and title
        title_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        title_frame.pack(fill=tk.X)
        
        icon_label = tk.Label(title_frame, text=icon, font=('Segoe UI', 14), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_frame, text=title, 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Amount
        amount_label = tk.Label(content_frame, text=amount, 
                                font=('Segoe UI', 28, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        amount_label.pack(anchor=tk.W, pady=(15, 8))
        
        # Change with arrow
        change_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        change_frame.pack(anchor=tk.W)
        
        arrow = "↑" if "+" in change else "↓" if "-" in change else ""
        arrow_label = tk.Label(change_frame, text=arrow, 
                                font=('Segoe UI', 10), 
                                bg=self.colors['bg_cards'], fg=color)
        arrow_label.pack(side=tk.LEFT)
        
        change_label = tk.Label(change_frame, text=change, 
                                font=('Segoe UI', 11), 
                                bg=self.colors['bg_cards'], fg=color)
        change_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Store references for updates
        card.amount_label = amount_label
        card.change_label = change_label
        card.arrow_label = arrow_label
        
        return card
    
    def create_charts_section(self):
        """Create charts section with dynamic resizing"""
        charts_frame = tk.Frame(self, bg=self.colors['bg_main'])
        charts_frame.grid(row=2, column=0, sticky='nsew', padx=30, pady=(0, 25))
        
        charts_frame.grid_columnconfigure(0, weight=1)
        charts_frame.grid_columnconfigure(1, weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Left chart - Income vs Expenses
        self.income_expense_chart_frame = tk.Frame(charts_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        self.income_expense_chart_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        
        chart_title1 = tk.Label(self.income_expense_chart_frame, text="📊 Income vs Expenses", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        chart_title1.pack(pady=25)
        
        # Right chart - Expense by Category
        self.category_chart_frame = tk.Frame(charts_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        self.category_chart_frame.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
        
        chart_title2 = tk.Label(self.category_chart_frame, text="🥧 Expense by Category", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        chart_title2.pack(pady=25)
    
    def create_recent_transactions(self):
        """Create recent transactions section"""
        transactions_frame = tk.Frame(self, bg=self.colors['bg_main'])
        transactions_frame.grid(row=3, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        self.transactions_container = tk.Frame(transactions_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        self.transactions_container.pack(fill=tk.X)
        
        trans_title = tk.Label(self.transactions_container, text="📋 Recent Transactions", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        trans_title.pack(anchor=tk.W, padx=25, pady=25)
        
        self.transactions_list = tk.Frame(self.transactions_container, bg=self.colors['bg_cards'])
        self.transactions_list.pack(fill=tk.X, padx=25, pady=(0, 25))
    
    def refresh_data(self):
        """Load and display dashboard data"""
        try:
            # Get current month and previous month
            current_month = get_current_month()
            prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
            
            # Get total income for current month
            income_query = """
                SELECT COALESCE(SUM(amount), 0) as total_income
                FROM transaction 
                WHERE user_id = %s AND type = 'Income' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            income_result = db.execute_query(income_query, (self.user_id, current_month))
            total_income = income_result[0][0] if income_result else 0
            
            # Get total income for previous month
            prev_income_result = db.execute_query(income_query, (self.user_id, prev_month))
            prev_income = prev_income_result[0][0] if prev_income_result else 0
            
            # Get total expenses for current month
            expense_query = """
                SELECT COALESCE(SUM(amount), 0) as total_expense
                FROM transaction 
                WHERE user_id = %s AND type = 'Expense' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            expense_result = db.execute_query(expense_query, (self.user_id, current_month))
            total_expense = expense_result[0][0] if expense_result else 0
            
            # Get total expenses for previous month
            prev_expense_result = db.execute_query(expense_query, (self.user_id, prev_month))
            prev_expense = prev_expense_result[0][0] if prev_expense_result else 0
            
            # Calculate balance
            balance = total_income - total_expense
            prev_balance = prev_income - prev_expense
            
            # Calculate percentage changes
            income_change = self.calculate_percentage_change(prev_income, total_income)
            expense_change = self.calculate_percentage_change(prev_expense, total_expense)
            balance_change = self.calculate_percentage_change(prev_balance, balance)
            
            # Update summary cards
            self.income_card.amount_label.config(text=format_currency(total_income))
            self.expense_card.amount_label.config(text=format_currency(total_expense))
            self.balance_card.amount_label.config(text=format_currency(balance))
            
            # Update change labels with arrows and percentages
            self.update_card_change(self.income_card, income_change, "from last month")
            self.update_card_change(self.expense_card, expense_change, "from last month")
            self.update_card_change(self.balance_card, balance_change, "Available balance")
            
            # Update balance color based on value
            if balance >= 0:
                self.balance_card.amount_label.config(fg=self.colors['accent_green'])
            else:
                self.balance_card.amount_label.config(fg=self.colors['accent_red'])
            
            # Load charts
            self.create_income_vs_expense_chart()
            self.create_expense_category_chart()
            
            # Load recent transactions
            self.load_recent_transactions()
                
        except Exception as e:
            show_error(f"Error loading dashboard data: {str(e)}")
    
    def calculate_percentage_change(self, old_value, new_value):
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 0 if new_value == 0 else 100
        return ((new_value - old_value) / old_value) * 100
    
    def update_card_change(self, card, change_percent, suffix):
        """Update card change label with percentage and arrow"""
        if change_percent > 0:
            arrow = "↑"
            color = self.colors['accent_green']
            sign = "+"
        elif change_percent < 0:
            arrow = "↓"
            color = self.colors['accent_red']
            sign = ""
        else:
            arrow = "→"
            color = self.colors['text_secondary']
            sign = ""
        
        change_text = f"{sign}{change_percent:.1f}% {suffix}"
        
        card.arrow_label.config(text=arrow, fg=color)
        card.change_label.config(text=change_text, fg=color)
    
    def create_income_vs_expense_chart(self):
        """Create income vs expense bar chart"""
        try:
            # Clear existing chart
            for widget in self.income_expense_chart_frame.winfo_children():
                if isinstance(widget, tk.Frame) and widget != self.income_expense_chart_frame.winfo_children()[0]:
                    widget.destroy()
            
            # Get data for last 6 months
            current_date = datetime.now()
            months_data = []
            
            for i in range(6):
                month_date = current_date - timedelta(days=30*i)
                month_str = month_date.strftime('%Y-%m')
                
                # Get income for this month
            income_query = """
                SELECT COALESCE(SUM(amount), 0) as total_income
                FROM transaction 
                WHERE user_id = %s AND type = 'Income' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            income_result = db.execute_query(income_query, (self.user_id, month_str))
            income = income_result[0][0] if income_result else 0
            
                # Get expenses for this month
            expense_query = """
                SELECT COALESCE(SUM(amount), 0) as total_expense
                FROM transaction 
                WHERE user_id = %s AND type = 'Expense' 
                AND DATE_FORMAT(date, '%%Y-%%m') = %s
            """
            expense_result = db.execute_query(expense_query, (self.user_id, month_str))
            expense = expense_result[0][0] if expense_result else 0
            
            months_data.append({
                'month': month_date.strftime('%b'),
                'income': float(income),
                'expense': float(expense)
            })
            
            # Reverse to show oldest to newest
            months_data.reverse()
            
            # Add demo data if no real data
            if not any(data['income'] > 0 or data['expense'] > 0 for data in months_data):
                demo_data = [
                    {'month': 'Jan', 'income': 5000, 'expense': 3200},
                    {'month': 'Feb', 'income': 4800, 'expense': 3800},
                    {'month': 'Mar', 'income': 5200, 'expense': 2900},
                    {'month': 'Apr', 'income': 4500, 'expense': 4100},
                    {'month': 'May', 'income': 5800, 'expense': 3600},
                    {'month': 'Jun', 'income': 5100, 'expense': 3300}
                ]
                months_data = demo_data
            
            # Create matplotlib figure
            fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors['bg_cards'])
            ax = fig.add_subplot(111, facecolor=self.colors['bg_cards'])
            
            months = [data['month'] for data in months_data]
            income_values = [data['income'] for data in months_data]
            expense_values = [data['expense'] for data in months_data]
            
            x = range(len(months))
            width = 0.35
            
            # Use theme colors
            income_color = self.colors['accent_green']
            expense_color = self.colors['accent_red']
            
            ax.bar([i - width/2 for i in x], income_values, width, label='Income', 
                    color=income_color, alpha=0.8, edgecolor='white', linewidth=1)
            ax.bar([i + width/2 for i in x], expense_values, width, label='Expense', 
                    color=expense_color, alpha=0.8, edgecolor='white', linewidth=1)
            
            ax.set_xlabel('Month', color=self.colors['text_primary'], fontsize=11)
            ax.set_ylabel('Amount ($)', color=self.colors['text_primary'], fontsize=11)
            ax.set_xticks(x)
            ax.set_xticklabels(months, color=self.colors['text_primary'])
            ax.tick_params(colors=self.colors['text_primary'])
            
            # Customize legend
            legend = ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
            legend.get_frame().set_facecolor(self.colors['bg_cards'])
            legend.get_frame().set_edgecolor(self.colors['border'])
            
            ax.grid(True, alpha=0.3, color=self.colors['border'])
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
            
            # Set background colors
            ax.spines['bottom'].set_color(self.colors['border'])
            ax.spines['top'].set_color(self.colors['border'])
            ax.spines['right'].set_color(self.colors['border'])
            ax.spines['left'].set_color(self.colors['border'])
            
            fig.tight_layout()
            
            # Display chart
            canvas = FigureCanvasTkAgg(fig, self.income_expense_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
        except Exception as e:
            error_label = tk.Label(self.income_expense_chart_frame, 
                                   text=f"Error loading chart: {str(e)}",
                                   font=('Segoe UI', 12), 
                                   bg=self.colors['bg_cards'], fg=self.colors['accent_red'])
            error_label.pack(pady=50)
    
    def create_expense_category_chart(self):
        """Create expense by category pie chart"""
        try:
            # Clear existing chart
            for widget in self.category_chart_frame.winfo_children():
                if isinstance(widget, tk.Frame) and widget != self.category_chart_frame.winfo_children()[0]:
                    widget.destroy()
            
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
            
            # Use demo data if no real data
            if not chart_result:
                demo_categories = ['Food & Dining', 'Transportation', 'Entertainment', 'Shopping', 'Bills']
                demo_amounts = [1200, 800, 600, 400, 300]
                categories = demo_categories
                amounts = demo_amounts
            else:
                categories = [row[0] for row in chart_result]
                amounts = [float(row[1]) for row in chart_result]
                
            # Create matplotlib figure
            fig = Figure(figsize=(6, 4), dpi=100, facecolor=self.colors['bg_cards'])
            ax = fig.add_subplot(111, facecolor=self.colors['bg_cards'])
            
            # Use theme colors
            colors = [self.colors['accent_red'], self.colors['accent_blue'], 
                      self.colors['accent_green'], '#f39c12', '#9b59b6', '#1abc9c']
            
            wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                             colors=colors[:len(categories)], startangle=90,
                                             textprops={'color': self.colors['text_primary'], 'fontsize': 10})
            
            # Customize text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            # Customize labels
            for text in texts:
                text.set_color(self.colors['text_primary'])
                text.set_fontsize(10)
                text.set_fontweight('bold')
                
            ax.axis('equal')
            
            fig.tight_layout()
            
            # Display chart
            canvas = FigureCanvasTkAgg(fig, self.category_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
        except Exception as e:
            error_label = tk.Label(self.category_chart_frame, 
                                   text=f"Error loading chart: {str(e)}",
                                   font=('Segoe UI', 12), 
                                   bg=self.colors['bg_cards'], fg=self.colors['accent_red'])
            error_label.pack(pady=50)
    
    def load_recent_transactions(self):
        """Load and display recent transactions"""
        try:
            # Clear existing transactions
            for widget in self.transactions_list.winfo_children():
                widget.destroy()
            
            # Get recent transactions
            query = """
                SELECT t.description, t.amount, t.type, t.date, c.category_name
                FROM transaction t
                LEFT JOIN category c ON t.category_id = c.category_id
                WHERE t.user_id = %s
                ORDER BY t.date DESC, t.transaction_id DESC
                LIMIT 5
            """
            
            result = db.execute_query(query, (self.user_id,))
            
            # Use demo data if no real data
            if not result:
                demo_transactions = [
                    ("Salary", 5000, "Income", datetime.now() - timedelta(days=1), "Salary"),
                    ("Grocery Shopping", 150, "Expense", datetime.now() - timedelta(days=2), "Food"),
                    ("Gas Station", 80, "Expense", datetime.now() - timedelta(days=3), "Transport"),
                    ("Freelance Work", 800, "Income", datetime.now() - timedelta(days=4), "Freelance"),
                    ("Netflix Subscription", 15, "Expense", datetime.now() - timedelta(days=5), "Entertainment")
                ]
                result = demo_transactions
            
            # Add Transaction List Headers
            header_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
            header_frame.pack(fill=tk.X, pady=(0, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Description Header
            tk.Label(header_frame, text="Description / Category", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=1, sticky='w', padx=(12, 0))
            # Date/Amount Header
            tk.Label(header_frame, text="Date / Amount", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=2, sticky='e')
            
            # Data Rows
            for i, (description, amount, trans_type, date, category) in enumerate(result):
                trans_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
                trans_frame.pack(fill=tk.X, pady=8)
                trans_frame.grid_columnconfigure(1, weight=1)
                
                # Icon based on type
                icon = "💰" if trans_type == 'Income' else "💸"
                
                # Amount color
                amount_color = self.colors['accent_green'] if trans_type == 'Income' else self.colors['accent_red']
                amount_prefix = "+" if trans_type == 'Income' else "-"
                
                # Icon (Column 0)
                icon_label = tk.Label(trans_frame, text=icon, font=('Segoe UI', 14), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
                icon_label.grid(row=0, column=0, rowspan=2, sticky='w', padx=(0, 12))
                
                # Description and category frame (Column 1 - expands)
                desc_label = tk.Label(trans_frame, text=description, 
                                     font=('Segoe UI', 13, 'bold'), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
                desc_label.grid(row=0, column=1, sticky='w')
                
                if category:
                    cat_label = tk.Label(trans_frame, text=category, 
                                         font=('Segoe UI', 11), 
                                         bg=self.colors['bg_cards'], fg=self.colors['text_secondary'])
                    cat_label.grid(row=1, column=1, sticky='w')
                
                # Date and amount (Column 2)
                date_label = tk.Label(trans_frame, text=date.strftime('%Y-%m-%d'), 
                                     font=('Segoe UI', 11), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary'])
                date_label.grid(row=0, column=2, sticky='e')
                
                amount_label = tk.Label(trans_frame, text=f"{amount_prefix}{format_currency(amount)}", 
                                       font=('Segoe UI', 13, 'bold'), 
                                       bg=self.colors['bg_cards'], fg=amount_color)
                amount_label.grid(row=1, column=2, sticky='e')
                
                # Add separator line (except for last item)
                if i < len(result) - 1:
                    separator = tk.Frame(self.transactions_list, height=1, bg=self.colors['border'])
                    separator.pack(fill=tk.X, pady=(12, 0))
            
        except Exception as e:
            error_label = tk.Label(self.transactions_list, 
                                   text=f"Error loading transactions: {str(e)}",
                                   font=('Segoe UI', 12), 
                                   bg=self.colors['bg_cards'], fg=self.colors['accent_red'])
            error_label.pack(pady=20)
    
# Transactions Frame
class TransactionsFrame(BaseFrame):
    def setup_frame(self):
        """Create transactions content"""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Add transaction button
        self.grid_rowconfigure(2, weight=1)  # Transactions list
        
        # Create sections
        self.create_header()
        self.create_add_transaction_section()
        self.create_transactions_list()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self, bg=self.colors['bg_main'])
        header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(25, 15))
        
        # Main title
        main_title = tk.Label(header_frame, text="Transactions", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        main_title.pack(anchor=tk.W, pady=(15, 8))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Manage your income and expenses", 
                            font=('Segoe UI', 15), 
                            bg=self.colors['bg_main'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor=tk.W)
    
    def create_add_transaction_section(self):
        """Create add transaction section"""
        add_frame = tk.Frame(self, bg=self.colors['bg_cards'], relief='groove', bd=1)
        add_frame.grid(row=1, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        # Title
        title = tk.Label(add_frame, text="📝 Add New Transaction", 
                        font=('Segoe UI', 16, 'bold'), 
                        bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title.pack(pady=25)
        
        # Form frame
        form_frame = tk.Frame(add_frame, bg=self.colors['bg_cards'])
        form_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        # Transaction Type
        type_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        type_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(type_frame, text="Type:", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.type_var = tk.StringVar(value="Expense")
        type_income = tk.Radiobutton(type_frame, text="Income", variable=self.type_var, 
                                    value="Income", font=('Segoe UI', 11),
                                    bg=self.colors['bg_cards'], fg=self.colors['text_primary'],
                                    selectcolor=self.colors['accent_green'],
                                    command=self.on_type_change)
        type_income.pack(side=tk.LEFT, padx=(20, 10))
        
        type_expense = tk.Radiobutton(type_frame, text="Expense", variable=self.type_var, 
                                     value="Expense", font=('Segoe UI', 11),
                                     bg=self.colors['bg_cards'], fg=self.colors['text_primary'],
                                     selectcolor=self.colors['accent_red'],
                                     command=self.on_type_change)
        type_expense.pack(side=tk.LEFT)
        
        # Category
        category_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        category_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(category_frame, text="Category:", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                         state="readonly", width=20, font=('Segoe UI', 11))
        self.category_combo.pack(side=tk.LEFT, padx=(20, 0))
        
        # Amount
        amount_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        amount_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(amount_frame, text="Amount ($):", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.amount_entry = tk.Entry(amount_frame, font=('Segoe UI', 11), width=25,
                                    bg=self.colors['bg_main'], fg=self.colors['text_primary'],
                                    insertbackground=self.colors['text_primary'])
        self.amount_entry.pack(side=tk.LEFT, padx=(20, 0))
        
        # Date
        date_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        date_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(date_frame, text="Date (YYYY-MM-DD):", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        self.date_entry = tk.Entry(date_frame, font=('Segoe UI', 11), width=25,
                                  bg=self.colors['bg_main'], fg=self.colors['text_primary'],
                                  insertbackground=self.colors['text_primary'])
        self.date_entry.pack(side=tk.LEFT, padx=(20, 0))
        
        # Description
        desc_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        desc_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(desc_frame, text="Description:", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(anchor=tk.W)
        
        self.description_text = tk.Text(desc_frame, width=50, height=3, font=('Segoe UI', 11),
                                       bg=self.colors['bg_main'], fg=self.colors['text_primary'],
                                       insertbackground=self.colors['text_primary'])
        self.description_text.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        buttons_frame = tk.Frame(form_frame, bg=self.colors['bg_cards'])
        buttons_frame.pack(fill=tk.X, pady=20)
        
        save_btn = tk.Button(buttons_frame, text="💾 Save Transaction", 
                           font=('Segoe UI', 12, 'bold'),
                           bg=self.colors['accent_green'], fg='white',
                           relief='flat', padx=20, pady=10,
                           command=self.save_transaction)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(buttons_frame, text="🗑️ Clear", 
                            font=('Segoe UI', 12, 'bold'),
                            bg=self.colors['accent_red'], fg='white',
                            relief='flat', padx=20, pady=10,
                            command=self.clear_form)
        clear_btn.pack(side=tk.LEFT)
        
        # Load categories and set default date
        self.load_categories()
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
    
    def create_transactions_list(self):
        """Create transactions list section"""
        list_frame = tk.Frame(self, bg=self.colors['bg_cards'], relief='groove', bd=1)
        list_frame.grid(row=2, column=0, sticky='nsew', padx=30, pady=(0, 25))
        
        # Title
        title = tk.Label(list_frame, text="📋 Recent Transactions", 
                        font=('Segoe UI', 16, 'bold'), 
                        bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title.pack(pady=25)
        
        # Transactions list
        self.transactions_list = tk.Frame(list_frame, bg=self.colors['bg_cards'])
        self.transactions_list.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
    
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
        transaction_type = self.type_var.get()
        
        try:
            if transaction_type == "Income":
                income_categories = ["Salary", "Freelance", "Investment", "Gift", "Other"]
                self.category_combo['values'] = income_categories
                if income_categories:
                    self.category_combo.set(income_categories[0])
            else:
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
            try:
                amount = float(amount_str)
                if amount <= 0:
                    show_error("Amount must be positive")
                    return
            except ValueError:
                show_error("Please enter a valid amount")
                return
            
            if not date_str:
                show_error("Please enter a date")
                return
            
            # Validate date
            try:
                transaction_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
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
                messagebox.showinfo("Success", "Transaction saved successfully!")
                self.clear_form()
                self.refresh_data()
            else:
                show_error("Failed to save transaction")
                
        except Exception as e:
            show_error(f"Error saving transaction: {str(e)}")
    
    def clear_form(self):
        """Clear the form"""
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.description_text.delete("1.0", tk.END)
    
    def refresh_data(self):
        """Load and display recent transactions"""
        try:
            # Clear existing transactions
            for widget in self.transactions_list.winfo_children():
                widget.destroy()
            
            # Get recent transactions
            query = """
                SELECT t.description, t.amount, t.type, t.date, c.category_name
                FROM transaction t
                LEFT JOIN category c ON t.category_id = c.category_id
                WHERE t.user_id = %s
                ORDER BY t.date DESC, t.transaction_id DESC
                LIMIT 10
            """
            
            result = db.execute_query(query, (self.user_id,))
            
            # Use demo data if no real data
            if not result:
                demo_transactions = [
                    ("Salary", 5000, "Income", datetime.now() - timedelta(days=1), "Salary"),
                    ("Grocery Shopping", 150, "Expense", datetime.now() - timedelta(days=2), "Food"),
                    ("Gas Station", 80, "Expense", datetime.now() - timedelta(days=3), "Transport"),
                    ("Freelance Work", 800, "Income", datetime.now() - timedelta(days=4), "Freelance"),
                    ("Netflix Subscription", 15, "Expense", datetime.now() - timedelta(days=5), "Entertainment")
                ]
                result = demo_transactions
            
            # Add Transaction List Headers
            header_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
            header_frame.pack(fill=tk.X, pady=(0, 10))
            header_frame.grid_columnconfigure(1, weight=1)
            
            # Description Header
            tk.Label(header_frame, text="Description / Category", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=1, sticky='w', padx=(12, 0))
            # Date/Amount Header
            tk.Label(header_frame, text="Date / Amount", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=2, sticky='e')
            
            # Data Rows
            for i, (description, amount, trans_type, date, category) in enumerate(result):
                trans_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
                trans_frame.pack(fill=tk.X, pady=8)
                trans_frame.grid_columnconfigure(1, weight=1)
                
                # Icon based on type
                icon = "💰" if trans_type == 'Income' else "💸"
                
                # Amount color
                amount_color = self.colors['accent_green'] if trans_type == 'Income' else self.colors['accent_red']
                amount_prefix = "+" if trans_type == 'Income' else "-"
                
                # Icon (Column 0)
                icon_label = tk.Label(trans_frame, text=icon, font=('Segoe UI', 14), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
                icon_label.grid(row=0, column=0, rowspan=2, sticky='w', padx=(0, 12))
                
                # Description and category frame (Column 1 - expands)
                desc_label = tk.Label(trans_frame, text=description, 
                                     font=('Segoe UI', 13, 'bold'), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
                desc_label.grid(row=0, column=1, sticky='w')
                
                if category:
                    cat_label = tk.Label(trans_frame, text=category, 
                                         font=('Segoe UI', 11), 
                                         bg=self.colors['bg_cards'], fg=self.colors['text_secondary'])
                    cat_label.grid(row=1, column=1, sticky='w')
                
                # Date and amount (Column 2)
                date_label = tk.Label(trans_frame, text=date.strftime('%Y-%m-%d'), 
                                     font=('Segoe UI', 11), 
                                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary'])
                date_label.grid(row=0, column=2, sticky='e')
                
                amount_label = tk.Label(trans_frame, text=f"{amount_prefix}{format_currency(amount)}", 
                                       font=('Segoe UI', 13, 'bold'), 
                                       bg=self.colors['bg_cards'], fg=amount_color)
                amount_label.grid(row=1, column=2, sticky='e')
                
                # Add separator line (except for last item)
                if i < len(result) - 1:
                    separator = tk.Frame(self.transactions_list, height=1, bg=self.colors['border'])
                    separator.pack(fill=tk.X, pady=(12, 0))
            
        except Exception as e:
            error_label = tk.Label(self.transactions_list, 
                                   text=f"Error loading transactions: {str(e)}",
                                   font=('Segoe UI', 12), 
                                   bg=self.colors['bg_cards'], fg=self.colors['accent_red'])
            error_label.pack(pady=20)

# Reports Frame
class ReportsFrame(BaseFrame):
    def setup_frame(self):
        """Create reports content"""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=0)  # Filters
        self.grid_rowconfigure(2, weight=1)  # Charts
        
        # Create sections
        self.create_header()
        self.create_filters_section()
        self.create_charts_section()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self, bg=self.colors['bg_main'])
        header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(25, 15))
        
        # Main title
        main_title = tk.Label(header_frame, text="Reports", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        main_title.pack(anchor=tk.W, pady=(15, 8))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Analyze your financial data with charts and insights", 
                            font=('Segoe UI', 15), 
                            bg=self.colors['bg_main'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor=tk.W)
    
    def create_filters_section(self):
        """Create filters section"""
        filters_frame = tk.Frame(self, bg=self.colors['bg_cards'], relief='groove', bd=1)
        filters_frame.grid(row=1, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        # Title
        title = tk.Label(filters_frame, text="📊 Chart Filters", 
                        font=('Segoe UI', 16, 'bold'), 
                        bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title.pack(pady=25)
        
        # Filters content
        content_frame = tk.Frame(filters_frame, bg=self.colors['bg_cards'])
        content_frame.pack(fill=tk.X, padx=25, pady=(0, 25))
        
        # Date range
        date_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        date_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(date_frame, text="Date Range:", font=('Segoe UI', 12, 'bold'), 
                bg=self.colors['bg_cards'], fg=self.colors['text_primary']).pack(side=tk.LEFT)
        
        tk.Label(date_frame, text="From:", font=('Segoe UI', 11), 
                bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(20, 5))
        
        self.from_date_var = tk.StringVar(value=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        self.from_date_entry = tk.Entry(date_frame, textvariable=self.from_date_var, width=12,
                                       font=('Segoe UI', 11), bg=self.colors['bg_main'], 
                                       fg=self.colors['text_primary'],
                                       insertbackground=self.colors['text_primary'])
        self.from_date_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(date_frame, text="To:", font=('Segoe UI', 11), 
                bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.to_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.to_date_entry = tk.Entry(date_frame, textvariable=self.to_date_var, width=12,
                                    font=('Segoe UI', 11), bg=self.colors['bg_main'], 
                                    fg=self.colors['text_primary'],
                                    insertbackground=self.colors['text_primary'])
        self.to_date_entry.pack(side=tk.LEFT)
        
        # Chart buttons
        buttons_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        buttons_frame.pack(fill=tk.X, pady=20)
        
        expense_pie_btn = tk.Button(buttons_frame, text="🥧 Expense Pie Chart", 
                                  font=('Segoe UI', 11, 'bold'),
                                  bg=self.colors['accent_red'], fg='white',
                                  relief='flat', padx=15, pady=8,
                                  command=self.show_expense_pie_chart)
        expense_pie_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        income_expense_btn = tk.Button(buttons_frame, text="📊 Income vs Expense", 
                                     font=('Segoe UI', 11, 'bold'),
                                     bg=self.colors['accent_blue'], fg='white',
                                     relief='flat', padx=15, pady=8,
                                     command=self.show_income_expense_chart)
        income_expense_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        category_bar_btn = tk.Button(buttons_frame, text="📈 Category Bar Chart", 
                                   font=('Segoe UI', 11, 'bold'),
                                   bg=self.colors['accent_green'], fg='white',
                                   relief='flat', padx=15, pady=8,
                                   command=self.show_category_bar_chart)
        category_bar_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_btn = tk.Button(buttons_frame, text="🗑️ Clear Charts", 
                            font=('Segoe UI', 11, 'bold'),
                            bg=self.colors['text_secondary'], fg='white',
                            relief='flat', padx=15, pady=8,
                            command=self.clear_charts)
        clear_btn.pack(side=tk.LEFT)
    
    def create_charts_section(self):
        """Create charts section"""
        charts_frame = tk.Frame(self, bg=self.colors['bg_cards'], relief='groove', bd=1)
        charts_frame.grid(row=2, column=0, sticky='nsew', padx=30, pady=(0, 25))
        
        # Title
        title = tk.Label(charts_frame, text="📈 Analytics Charts", 
                        font=('Segoe UI', 16, 'bold'), 
                        bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title.pack(pady=25)
        
        # Chart display area
        self.chart_frame = tk.Frame(charts_frame, bg=self.colors['bg_cards'])
        self.chart_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
        
        # Initialize chart generator
        self.chart_generator = None
    
    def show_expense_pie_chart(self):
        """Show expense pie chart"""
        try:
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
                    from utils.charts import ChartGenerator
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
                    from utils.charts import ChartGenerator
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
                    from utils.charts import ChartGenerator
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
    
    def refresh_data(self):
        """Refresh reports data"""
        pass

# Settings Frame
class SettingsFrame(BaseFrame):
    def setup_frame(self):
        """Create settings content"""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Settings content
        
        # Create sections
        self.create_header()
        self.create_settings_content()
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self, bg=self.colors['bg_main'])
        header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(25, 15))
        
        # Main title
        main_title = tk.Label(header_frame, text="Settings", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        main_title.pack(anchor=tk.W, pady=(15, 8))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Configure your application preferences", 
                            font=('Segoe UI', 15), 
                            bg=self.colors['bg_main'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor=tk.W)
    
    def create_settings_content(self):
        """Create settings content"""
        settings_frame = tk.Frame(self, bg=self.colors['bg_cards'], relief='groove', bd=1)
        settings_frame.grid(row=1, column=0, sticky='nsew', padx=30, pady=(0, 25))
        
        # Title
        title = tk.Label(settings_frame, text="⚙️ Application Settings", 
                        font=('Segoe UI', 16, 'bold'), 
                        bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title.pack(pady=25)
        
        # Settings content
        content_frame = tk.Frame(settings_frame, bg=self.colors['bg_cards'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 25))
        
        # Coming soon message
        coming_soon = tk.Label(content_frame, text="🚧 Settings Panel Coming Soon!", 
                              font=('Segoe UI', 18, 'bold'), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_secondary'])
        coming_soon.pack(expand=True)
        
        # Description
        description = tk.Label(content_frame, text="This section will include:\n• Theme preferences\n• Notification settings\n• Data export options\n• Account management", 
                              font=('Segoe UI', 12), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_secondary'],
                              justify=tk.LEFT)
        description.pack(pady=20)
    
    def refresh_data(self):
        """Refresh settings data"""
        pass

class DashboardWindow:
    def __init__(self, user_id, parent_window=None):
        self.user_id = user_id
        self.parent_window = parent_window
        
        # Create main window
        self.root = tk.Toplevel() if parent_window else tk.Tk()
        self.root.title("FinanceFlow - Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 650)
        self.root.resizable(True, True)
        
        # Initialize theme colors
        self.init_theme_colors()
        
        # Center the window
        self.center_window()
        
        # Configure styles
        self.configure_styles()
        
        # Create main layout
        self.create_main_layout()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area with frame container
        self.create_main_content()
        
        # Initialize frames
        self.frames = {}
        self.current_frame = None
        
        # Create all frames
        self.create_frames()
        
        # Show dashboard frame by default
        self.show_frame('dashboard')
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_theme_colors(self):
        """Initialize theme colors for dark mode only"""
        self.colors = {
            'bg_main': '#1e293b',
            'bg_sidebar': '#0f766e',  # Teal color for sidebar
            'bg_cards': '#334155',
            'text_primary': '#f1f5f9',
            'text_secondary': '#cbd5e1',
            'text_sidebar': '#ffffff',
            'accent_green': '#22c55e',
            'accent_red': '#ef4444',
            'accent_blue': '#3b82f6',
            'border': '#475569',
            'shadow': '#00000030'
        }
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = 1200
        height = 800
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def configure_styles(self):
        """Configure ttk styles for modern look"""
        style = ttk.Style()
        
        # Configure sidebar button style
        style.configure("Sidebar.TButton",
                       background=self.colors['bg_sidebar'],
                       foreground=self.colors['text_sidebar'],
                       font=('Segoe UI', 11),
                       padding=(20, 12),
                       relief="flat",
                       borderwidth=0)
        
        style.map("Sidebar.TButton",
                 background=[('active', '#0d9488'),
                           ('pressed', '#0a7a80')])
        
        # Configure active sidebar button
        style.configure("ActiveSidebar.TButton",
                       background="#0d9488",
                       foreground=self.colors['text_sidebar'],
                       font=('Segoe UI', 11, 'bold'),
                       padding=(20, 12),
                       relief="flat",
                       borderwidth=0)
        
        # Configure card style
        style.configure("Card.TFrame",
                        background=self.colors['bg_cards'],
                        relief="groove",
                        borderwidth=1)
        
        # Configure summary card labels
        style.configure("SummaryTitle.TLabel",
                        background=self.colors['bg_cards'],
                        foreground=self.colors['text_primary'],
                        font=('Segoe UI', 11, 'bold'))
        
        style.configure("SummaryAmount.TLabel",
                        background=self.colors['bg_cards'],
                        foreground=self.colors['text_primary'],
                        font=('Segoe UI', 20, 'bold'))
        
        style.configure("SummaryChange.TLabel",
                        background=self.colors['bg_cards'],
                        font=('Segoe UI', 10))
        
        # Configure section titles
        style.configure("SectionTitle.TLabel",
                        background=self.colors['bg_main'],
                        foreground=self.colors['text_primary'],
                        font=('Segoe UI', 16, 'bold'))
        
    
    # --- Dynamic Layout Refactor ---
    def create_main_layout(self):
        """Create main layout using grid with weights for dynamic resizing"""
        # Main container is the root window
        self.root.grid_columnconfigure(0, weight=0) # Sidebar column (fixed width)
        self.root.grid_columnconfigure(1, weight=1) # Content area column (expands)
        self.root.grid_rowconfigure(0, weight=1)    # Single row for content (expands)
        
        # Sidebar (fixed width, sticky N/S)
        self.sidebar = tk.Frame(self.root, bg=self.colors['bg_sidebar'], width=260)
        self.sidebar.grid(row=0, column=0, sticky='nsew')
        self.sidebar.grid_propagate(False) # Keep sidebar width fixed
        
        # Main content area (expands, sticky N/S/E/W)
        self.content_area = tk.Frame(self.root, bg=self.colors['bg_main'])
        self.content_area.grid(row=0, column=1, sticky='nsew')
    # --- End Dynamic Layout Refactor ---
    
    def create_sidebar(self):
        """Create sidebar navigation"""
        # ... (Sidebar creation code remains the same, using pack for internal widgets) ...
        # Logo and title
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        logo_frame.pack(fill=tk.X, padx=25, pady=(30, 30))
        
        # Logo icon
        logo_icon = tk.Label(logo_frame, text="💰", font=('Segoe UI', 28), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        logo_icon.pack()
        
        # App name
        app_name = tk.Label(logo_frame, text="FinanceFlow", 
                            font=('Segoe UI', 18, 'bold'), 
                            bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        app_name.pack()
        
        # Tagline
        tagline = tk.Label(logo_frame, text="Track your finances", 
                            font=('Segoe UI', 11), 
                            bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        tagline.pack()
        
        # Navigation section
        nav_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        nav_frame.pack(fill=tk.X, padx=25, pady=(0, 20))
        
        nav_title = tk.Label(nav_frame, text="Navigation", 
                             font=('Segoe UI', 13, 'bold'), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        nav_title.pack(anchor=tk.W, pady=(0, 15))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        # Dashboard button (active by default)
        self.nav_buttons['dashboard'] = ttk.Button(nav_frame, text="📊 Dashboard", 
                                                    style="ActiveSidebar.TButton",
                                                    command=lambda: self.navigate_to('dashboard'))
        self.nav_buttons['dashboard'].pack(fill=tk.X, pady=3)
        
        # Transactions button
        self.nav_buttons['transactions'] = ttk.Button(nav_frame, text="📝 Transactions", 
                                                     style="Sidebar.TButton",
                                                     command=lambda: self.navigate_to('transactions'))
        self.nav_buttons['transactions'].pack(fill=tk.X, pady=3)
        
        # Reports button
        self.nav_buttons['reports'] = ttk.Button(nav_frame, text="📈 Reports", 
                                                 style="Sidebar.TButton",
                                                 command=lambda: self.navigate_to('reports'))
        self.nav_buttons['reports'].pack(fill=tk.X, pady=3)
        
        # Settings button
        self.nav_buttons['settings'] = ttk.Button(nav_frame, text="⚙️ Settings", 
                                                 style="Sidebar.TButton",
                                                 command=lambda: self.navigate_to('settings'))
        self.nav_buttons['settings'].pack(fill=tk.X, pady=3)
        
        # Profile section at bottom
        profile_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
        profile_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=25, pady=20)
        
        # Profile info
        profile_info = tk.Frame(profile_frame, bg=self.colors['bg_sidebar'])
        profile_info.pack(fill=tk.X, pady=(0, 15))
        
        # User avatar
        avatar = tk.Label(profile_info, text="👤", font=('Segoe UI', 16), 
                             bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        avatar.pack(side=tk.LEFT)
        
        # User info
        user_info = tk.Frame(profile_info, bg=self.colors['bg_sidebar'])
        user_info.pack(side=tk.LEFT, padx=(10, 0))
        
        self.username_label = tk.Label(user_info, text="Welcome, User", 
                                      font=('Segoe UI', 11, 'bold'), 
                                      bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        self.username_label.pack(anchor=tk.W)
        
        user_role = tk.Label(user_info, text="Finance Manager", 
                            font=('Segoe UI', 9), 
                            bg=self.colors['bg_sidebar'], fg=self.colors['text_sidebar'])
        user_role.pack(anchor=tk.W)
        
        # Logout button
        logout_btn = ttk.Button(profile_frame, text="🚪 Logout", 
                                 style="Sidebar.TButton",
                                 command=self.logout)
        logout_btn.pack(fill=tk.X)
    
    def create_main_content(self):
        """Create main content area with frame container"""
        # Configure content area grid weights
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)
        
        # Create frame container
        self.frame_container = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        self.frame_container.grid(row=0, column=0, sticky='nsew')
    
    def create_frames(self):
        """Create all application frames"""
        # Create dashboard frame
        self.frames['dashboard'] = DashboardFrame(self.frame_container, self.user_id, self.colors)
        
        # Create transactions frame
        self.frames['transactions'] = TransactionsFrame(self.frame_container, self.user_id, self.colors)
        
        # Create reports frame
        self.frames['reports'] = ReportsFrame(self.frame_container, self.user_id, self.colors)
        
        # Create settings frame
        self.frames['settings'] = SettingsFrame(self.frame_container, self.user_id, self.colors)
    
    def show_frame(self, frame_name):
        """Show the specified frame"""
        # Hide current frame
        if self.current_frame:
            self.current_frame.grid_remove()
        
        # Show new frame
        if frame_name in self.frames:
            self.current_frame = self.frames[frame_name]
            self.current_frame.grid(row=0, column=0, sticky='nsew')
            
            # Refresh frame data
            self.current_frame.refresh_data()
            
            # Update window title
            titles = {
                'dashboard': 'FinanceFlow - Dashboard',
                'transactions': 'FinanceFlow - Transactions',
                'reports': 'FinanceFlow - Reports',
                'settings': 'FinanceFlow - Settings'
            }
            self.root.title(titles.get(frame_name, 'FinanceFlow'))
    
    def create_header(self):
        """Create header section"""
        header_frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        # Use grid instead of pack
        header_frame.grid(row=0, column=0, sticky='ew', padx=30, pady=(25, 15))
        
        # Internal elements still use pack, which is fine for simple horizontal/vertical layout
        top_frame = tk.Frame(header_frame, bg=self.colors['bg_main'])
        top_frame.pack(fill=tk.X)
        
        # App icon and title
        title_frame = tk.Frame(top_frame, bg=self.colors['bg_main'])
        title_frame.pack(side=tk.LEFT)
        
        app_icon = tk.Label(title_frame, text="💰", font=('Segoe UI', 18), 
                            bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        app_icon.pack(side=tk.LEFT)
        
        app_title = tk.Label(title_frame, text="FinanceFlow", 
                             font=('Segoe UI', 18, 'bold'), 
                             bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        app_title.pack(side=tk.LEFT, padx=(10, 0))
        
        
        # Main title
        main_title = tk.Label(header_frame, text="Dashboard", 
                              font=('Segoe UI', 32, 'bold'), 
                              bg=self.colors['bg_main'], fg=self.colors['text_primary'])
        main_title.pack(anchor=tk.W, pady=(15, 8))
        
        # Subtitle
        subtitle = tk.Label(header_frame, text="Overview of your financial activity", 
                            font=('Segoe UI', 15), 
                            bg=self.colors['bg_main'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor=tk.W)
    
    def create_summary_cards(self):
        """Create summary cards for financial overview"""
        cards_frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        # Use grid instead of pack
        cards_frame.grid(row=1, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        # Center the cards (internal centering uses pack/expand=True which works)
        cards_container = tk.Frame(cards_frame, bg=self.colors['bg_main'])
        cards_container.pack(expand=True)
        
        # Cards remain fixed size, so pack side=tk.LEFT is fine
        self.income_card = self.create_summary_card(cards_container, "Total Income", "$0.00", 
                                                    "+0% from last month", self.colors['accent_green'], "📈")
        self.income_card.pack(side=tk.LEFT, padx=(0, 15))
        
        self.expense_card = self.create_summary_card(cards_container, "Total Expenses", "$0.00", 
                                                     "+0% from last month", self.colors['accent_red'], "📉")
        self.expense_card.pack(side=tk.LEFT, padx=(0, 15))
        
        self.balance_card = self.create_summary_card(cards_container, "Balance", "$0.00", 
                                                     "Available balance", self.colors['accent_blue'], "💰")
        self.balance_card.pack(side=tk.LEFT)
    
    def create_summary_card(self, parent, title, amount, change, color, icon):
        """Create a summary card"""
        card = tk.Frame(parent, bg=self.colors['bg_cards'], relief='groove', bd=1)
        # card.pack_propagate(False) # Removed as pack_propagate is set on create_main_layout sidebar
        card.configure(width=220, height=140)
        
        # Card content
        content_frame = tk.Frame(card, bg=self.colors['bg_cards'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Icon and title
        title_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        title_frame.pack(fill=tk.X)
        
        icon_label = tk.Label(title_frame, text=icon, font=('Segoe UI', 14), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(title_frame, text=title, 
                              font=('Segoe UI', 12, 'bold'), 
                              bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Amount
        amount_label = tk.Label(content_frame, text=amount, 
                                font=('Segoe UI', 28, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        amount_label.pack(anchor=tk.W, pady=(15, 8))
        
        # Change with arrow
        change_frame = tk.Frame(content_frame, bg=self.colors['bg_cards'])
        change_frame.pack(anchor=tk.W)
        
        arrow = "↑" if "+" in change else "↓" if "-" in change else ""
        arrow_label = tk.Label(change_frame, text=arrow, 
                                font=('Segoe UI', 10), 
                                bg=self.colors['bg_cards'], fg=color)
        arrow_label.pack(side=tk.LEFT)
        
        change_label = tk.Label(change_frame, text=change, 
                                font=('Segoe UI', 11), 
                                bg=self.colors['bg_cards'], fg=color)
        change_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Store references for updates
        card.amount_label = amount_label
        card.change_label = change_label
        card.arrow_label = arrow_label
        
        return card
    
    def create_charts_section(self):
        """Create charts section with dynamic resizing"""
        charts_frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        # Use grid and sticky='nsew' to expand
        charts_frame.grid(row=2, column=0, sticky='nsew', padx=30, pady=(0, 25))
        
        # Configure charts frame grid weights
        charts_frame.grid_columnconfigure(0, weight=1) # Left chart column expands
        charts_frame.grid_columnconfigure(1, weight=1) # Right chart column expands
        charts_frame.grid_rowconfigure(0, weight=1)    # Single row for charts expands
        
        # Left chart - Income vs Expenses
        self.income_expense_chart_frame = tk.Frame(charts_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        # Use grid and sticky='nsew'
        self.income_expense_chart_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
        
        chart_title1 = tk.Label(self.income_expense_chart_frame, text="📊 Income vs Expenses", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        chart_title1.pack(pady=25)
        
        # Right chart - Expense by Category
        self.category_chart_frame = tk.Frame(charts_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        # Use grid and sticky='nsew'
        self.category_chart_frame.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
        
        chart_title2 = tk.Label(self.category_chart_frame, text="🥧 Expense by Category", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        chart_title2.pack(pady=25)
    
    def create_recent_transactions(self):
        """Create recent transactions section"""
        transactions_frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        # Use grid instead of pack
        transactions_frame.grid(row=3, column=0, sticky='ew', padx=30, pady=(0, 25))
        
        # Transactions container
        self.transactions_container = tk.Frame(transactions_frame, bg=self.colors['bg_cards'], relief='groove', bd=1)
        self.transactions_container.pack(fill=tk.X)
        
        # Title
        trans_title = tk.Label(self.transactions_container, text="📋 Recent Transactions", 
                                font=('Segoe UI', 16, 'bold'), 
                                bg=self.colors['bg_cards'], fg=self.colors['text_primary'])
        trans_title.pack(anchor=tk.W, padx=25, pady=25)
        
        # Transactions list
        self.transactions_list = tk.Frame(self.transactions_container, bg=self.colors['bg_cards'])
        self.transactions_list.pack(fill=tk.X, padx=25, pady=(0, 25))
    # --- End Dynamic Content Area Refactor ---
    
    
    def navigate_to(self, page):
        """Handle navigation between pages"""
        # Update button styles
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == page:
                btn.configure(style="ActiveSidebar.TButton")
            else:
                btn.configure(style="Sidebar.TButton")
        
        # Show the requested frame
        self.show_frame(page)
    
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
    # NOTE: You must have a database connection and a user with user_id=1 for this to run
    dashboard = DashboardWindow(1)
    dashboard.show()
