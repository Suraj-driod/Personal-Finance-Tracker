import mysql.connector
from mysql.connector import Error
import os
from typing import Optional

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.host = "localhost"
        self.user = "root"
        self.password = "admin"  # Change this to your MySQL password
        self.database = "finance_tracker"
    
    def get_connection(self):
        """Get MySQL database connection"""
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=True
                )
                print("Successfully connected to MySQL database")
            return self.connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute(query, params)
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    cursor.close()
                    return result
                else:
                    cursor.close()
                    return True
        except Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_many(self, query: str, params_list: list):
        """Execute a query with multiple parameter sets"""
        try:
            connection = self.get_connection()
            if connection:
                cursor = connection.cursor()
                cursor.executemany(query, params_list)
                cursor.close()
                return True
        except Error as e:
            print(f"Error executing batch query: {e}")
            return None

# Global database instance
db = DatabaseConnection()

def get_connection():
    """Get database connection instance"""
    return db.get_connection()

def close_connection():
    """Close database connection"""
    db.close_connection()
