import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import tkinter as tk
from tkinter import ttk

class ChartGenerator:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.figure = None
        self.canvas = None
        
        # Set matplotlib style
        plt.style.use('default')
        
    def create_pie_chart(self, data: Dict[str, float], title: str = "Expense by Category") -> Figure:
        """Create a pie chart for expense categories"""
        if not data:
            return None
            
        # Create figure
        fig = Figure(figsize=(8, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data
        labels = list(data.keys())
        sizes = list(data.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        # Customize text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        return fig
    
    def create_line_chart(self, data: List[Tuple[datetime, float]], title: str = "Monthly Trend") -> Figure:
        """Create a line chart for monthly trends"""
        if not data:
            return None
            
        # Create figure
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data
        dates = [item[0] for item in data]
        amounts = [item[1] for item in data]
        
        # Create line chart
        ax.plot(dates, amounts, marker='o', linewidth=2, markersize=6)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Customize chart
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def create_bar_chart(self, data: Dict[str, float], title: str = "Category Comparison") -> Figure:
        """Create a bar chart for category comparison"""
        if not data:
            return None
            
        # Create figure
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        # Prepare data
        categories = list(data.keys())
        amounts = list(data.values())
        colors = plt.cm.viridis(range(len(categories)))
        
        # Create bar chart
        bars = ax.bar(categories, amounts, color=colors, alpha=0.7)
        
        # Add value labels on bars
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(amounts)*0.01,
                   f'${amount:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Customize chart
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Category', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        
        # Rotate x-axis labels if needed
        if len(max(categories, key=len)) > 8:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add grid
        ax.grid(True, alpha=0.3, axis='y')
        
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def create_income_expense_chart(self, income_data: List[Tuple[datetime, float]], 
                                  expense_data: List[Tuple[datetime, float]], 
                                  title: str = "Income vs Expense Trend") -> Figure:
        """Create a dual-line chart for income vs expense comparison"""
        # Create figure
        fig = Figure(figsize=(12, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        if income_data:
            income_dates = [item[0] for item in income_data]
            income_amounts = [item[1] for item in income_data]
            ax.plot(income_dates, income_amounts, marker='o', linewidth=2, 
                   markersize=6, label='Income', color='green')
        
        if expense_data:
            expense_dates = [item[0] for item in expense_data]
            expense_amounts = [item[1] for item in expense_data]
            ax.plot(expense_dates, expense_amounts, marker='s', linewidth=2, 
                   markersize=6, label='Expense', color='red')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        # Customize chart
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Adjust layout
        fig.tight_layout()
        
        return fig
    
    def display_chart(self, fig: Figure, row: int = 0, column: int = 0):
        """Display chart in the parent frame"""
        if fig is None:
            return
            
        # Clear existing canvas
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        
        # Create new canvas
        self.canvas = FigureCanvasTkAgg(fig, self.parent_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=row, column=column, sticky='nsew')
        
        # Store figure reference
        self.figure = fig
    
    def clear_chart(self):
        """Clear the displayed chart"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            plt.close(self.figure)
            self.figure = None

def create_simple_pie_chart(categories: List[str], amounts: List[float], 
                           title: str = "Expense Distribution") -> Figure:
    """Create a simple pie chart with given data"""
    if not categories or not amounts:
        return None
        
    fig = Figure(figsize=(8, 6), dpi=100)
    ax = fig.add_subplot(111)
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%', 
                                     startangle=90, colors=plt.cm.Set3(range(len(categories))))
    
    # Customize text
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.axis('equal')
    
    return fig
