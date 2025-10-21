# Personal Finance Tracker

A comprehensive personal finance management application built with Python Tkinter and MySQL. Track your income, expenses, manage budgets, and analyze your financial data with beautiful charts and reports.

## Features

### 🔐 User Authentication
- Secure login and registration system
- Password hashing for security
- User session management

### 💰 Transaction Management
- Add income and expense transactions
- Categorize transactions (Food, Transportation, Entertainment, etc.)
- Date-based transaction tracking
- Transaction descriptions

### 📊 Budget Management
- Set monthly budget limits
- Visual progress tracking with progress bars
- Overspending alerts
- Budget vs actual spending analysis

### 📈 Financial Reports & Analytics
- Interactive charts and graphs
- Expense distribution (pie charts)
- Income vs Expense trends (line charts)
- Category-wise comparisons (bar charts)
- Export data to CSV
- Date range filtering

### 🎨 Modern GUI
- Clean, intuitive interface
- Responsive design
- Color-coded financial data
- Easy navigation between features

## Tech Stack

- **Frontend:** Python Tkinter (GUI)
- **Backend:** MySQL Database
- **Analytics:** Matplotlib (charts), Pandas (data processing)
- **Database Connector:** mysql-connector-python

## Installation

### Prerequisites

1. **Python 3.7+** - [Download Python](https://www.python.org/downloads/)
2. **MySQL Server** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd finance_tracker
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup MySQL Database**
   
   a. Start MySQL server
   
   b. Create database and user:
   ```sql
   CREATE DATABASE finance_tracker;
   CREATE USER 'finance_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON finance_tracker.* TO 'finance_user'@'localhost';
   FLUSH PRIVILEGES;
   ```
   
   c. Import database schema:
   ```bash
   mysql -u finance_user -p finance_tracker < db/setup.sql
   ```

4. **Configure Database Connection**
   
   Edit `db/connection.py` and update the connection parameters:
   ```python
   self.host = "localhost"
   self.user = "finance_user"  # or your MySQL username
   self.password = "your_password"  # your MySQL password
   self.database = "finance_tracker"
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```

## Usage

### Getting Started

1. **First Time Setup**
   - Run the application
   - Register a new account
   - Login with your credentials

2. **Adding Transactions**
   - Click "Add Transaction" from dashboard
   - Select transaction type (Income/Expense)
   - Choose category and enter amount
   - Add description and date
   - Save transaction

3. **Setting Budget**
   - Click "Manage Budget" from dashboard
   - Set monthly budget limit
   - Monitor spending progress
   - Get alerts for overspending

4. **Viewing Reports**
   - Click "View Reports" from dashboard
   - Apply date filters
   - Generate charts and analytics
   - Export data to CSV

### Default Categories

The application comes with pre-configured categories:

**Income Categories:**
- Salary
- Freelance
- Investment
- Gift
- Other

**Expense Categories:**
- Food
- Transportation
- Entertainment
- Healthcare
- Education
- Shopping
- Bills
- Rent
- Utilities
- Travel
- Other

## Project Structure

```
finance_tracker/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── db/
│   ├── connection.py      # Database connection handler
│   └── setup.sql         # Database schema and initial data
├── ui/
│   ├── login_page.py      # Login and registration
│   ├── dashboard.py       # Main dashboard
│   ├── add_transaction.py # Transaction form
│   ├── budget_page.py     # Budget management
│   └── reports_page.py    # Reports and analytics
├── utils/
│   ├── helpers.py         # Utility functions
│   └── charts.py          # Chart generation
└── assets/
    └── icons/             # Application icons (optional)
```

## Database Schema

### Tables

- **user** - User accounts and authentication
- **category** - Transaction categories
- **transaction** - Income and expense records
- **budget** - Monthly budget limits

### Key Features

- Foreign key relationships for data integrity
- Indexed columns for optimal performance
- Automatic timestamps for audit trails
- Cascade deletes for data cleanup

## Customization

### Adding New Categories

1. Edit `db/setup.sql` to add new categories
2. Run the SQL script to update database
3. Restart the application

### Modifying Charts

Edit `utils/charts.py` to:
- Change chart colors and styles
- Add new chart types
- Modify chart layouts

### Styling the Interface

The application uses Tkinter's ttk (themed) widgets. You can:
- Modify colors in individual UI files
- Add custom themes
- Change fonts and sizes

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Verify MySQL server is running
   - Check connection credentials in `db/connection.py`
   - Ensure database exists and user has permissions

2. **Import Errors**
   - Install all required packages: `pip install -r requirements.txt`
   - Check Python version (3.7+ required)

3. **Chart Display Issues**
   - Ensure matplotlib backend is properly configured
   - Check if display is available (for headless systems)

4. **Permission Errors**
   - Ensure MySQL user has proper privileges
   - Check file permissions for CSV exports

### Getting Help

- Check the console output for error messages
- Verify database connection with MySQL client
- Test individual components by running them separately

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Version History

- **v1.0** - Initial release with core features
  - User authentication
  - Transaction management
  - Budget tracking
  - Basic reporting and charts

---

**Happy Financial Tracking! 💰📊**
