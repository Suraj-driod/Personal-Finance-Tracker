-- Personal Finance Tracker Database Setup
-- Run this script to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS finance_tracker;
USE finance_tracker;

-- Create user table
CREATE TABLE IF NOT EXISTS user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create category table
CREATE TABLE IF NOT EXISTS category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL
);

-- Create transaction table
CREATE TABLE IF NOT EXISTS transaction (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    type ENUM('Income', 'Expense') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES category(category_id) ON DELETE RESTRICT
);

-- Create budget table
CREATE TABLE IF NOT EXISTS budget (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    month VARCHAR(20) NOT NULL,
    limit_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_month (user_id, month)
);

-- Insert default categories
INSERT IGNORE INTO category (category_name) VALUES 
('Food'),
('Transportation'),
('Entertainment'),
('Healthcare'),
('Education'),
('Shopping'),
('Bills'),
('Rent'),
('Utilities'),
('Travel'),
('Salary'),
('Freelance'),
('Investment'),
('Gift'),
('Other');

-- Create indexes for better performance
CREATE INDEX idx_transaction_user_date ON transaction(user_id, date);
CREATE INDEX idx_transaction_type ON transaction(type);
CREATE INDEX idx_budget_user_month ON budget(user_id, month);
