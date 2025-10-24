import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
# Assuming these imports are correct and available
from db.connection import db
from utils.helpers import format_currency, get_current_month, show_error
from utils.charts import ChartGenerator
from ui.add_transaction import AddTransactionWindow
from ui.budget_page import BudgetWindow
from ui.reports_page import ReportsWindow
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter.font as tkFont

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
        
        # Create main layout (Refactored to use grid for dynamic sizing)
        self.create_main_layout()
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
        # Load dashboard data
        self.load_dashboard_data()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def init_theme_colors(self):
        """Initialize theme colors for dark mode only"""
        self.colors = {
            'bg_main': '#1e293b',
            'bg_sidebar': '#0B7A75',  # Teal color for sidebar
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
    
    # --- Dynamic Content Area Refactor ---
    def create_main_content(self):
        """Create main content area using grid for dynamic resizing"""
        # Configure content area grid weights:
        self.content_area.grid_columnconfigure(0, weight=1) # Single column in content area expands
        self.content_area.grid_rowconfigure(0, weight=0) # Header (fixed height)
        self.content_area.grid_rowconfigure(1, weight=0) # Summary Cards (fixed height)
        self.content_area.grid_rowconfigure(2, weight=1) # Charts section (expands vertically)
        self.content_area.grid_rowconfigure(3, weight=0) # Recent transactions (fixed height)
        
        # Header
        self.create_header()
        
        # Summary cards
        self.create_summary_cards()
        
        # Charts section
        self.create_charts_section()
        
        # Recent transactions
        self.create_recent_transactions()
    
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
        
        # Handle page navigation
        if page == 'transactions':
            self.open_add_transaction()
        elif page == 'reports':
            self.open_reports()
        elif page == 'settings':
            # For now, just show a message
            messagebox.showinfo("Settings", "Settings page coming soon!")
    
    def create_income_vs_expense_chart(self):
        """Create income vs expense bar chart"""
        try:
            # Clear existing chart
            for widget in self.income_expense_chart_frame.winfo_children():
                # Only destroy the old canvas frame, keep the title label
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
            
            # Add Transaction List Headers (Optional but helpful)
            header_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
            header_frame.pack(fill=tk.X, pady=(0, 10))
            header_frame.grid_columnconfigure(1, weight=1) # The description column expands
            
            # Description Header
            tk.Label(header_frame, text="Description / Category", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=1, sticky='w', padx=(12, 0))
            # Date/Amount Header
            tk.Label(header_frame, text="Date / Amount", font=('Segoe UI', 11, 'bold'), 
                     bg=self.colors['bg_cards'], fg=self.colors['text_secondary']).grid(row=0, column=2, sticky='e')
            
            # Data Rows
            for i, (description, amount, trans_type, date, category) in enumerate(result):
                # Create transaction item
                trans_frame = tk.Frame(self.transactions_list, bg=self.colors['bg_cards'])
                trans_frame.pack(fill=tk.X, pady=8)
                trans_frame.grid_columnconfigure(1, weight=1) # The description column expands
                
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
    
    # ... (Rest of the class methods remain the same) ...
    def load_dashboard_data(self):
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
    # NOTE: You must have a database connection and a user with user_id=1 for this to run
    dashboard = DashboardWindow(1)
    dashboard.show()
