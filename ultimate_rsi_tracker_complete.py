#!/usr/bin/env python3
"""
Ultimate Enhanced RSI Tracker - COMPLETE WORKING VERSION
🔧 FIXES: Tkinter widget destruction issue that breaks chart loading after first use

FIXED ISSUES:
- Widget reference errors after first chart load
- Improved chart clearing logic
- Better error handling for delisted stocks

Author: Claude (Widget Fix Version)
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yfinance as yf
import pandas as pd
import numpy as np
import threading
import time
from datetime import datetime, timedelta
import json
import os
import webbrowser
import csv
from typing import Dict, List, Optional

# Chart imports
CHARTS_AVAILABLE = False
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    plt.style.use('dark_background')
    CHARTS_AVAILABLE = True
    print("✅ Charts available")
except ImportError:
    print("⚠️ Charts not available - install matplotlib")
    CHARTS_AVAILABLE = False

class RSICalculator:
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        if len(prices) < period + 1:
            return pd.Series([50.0] * len(prices), index=prices.index)
        
        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0)
        losses = -deltas.where(deltas < 0, 0)
        
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50.0)

class FixedStockData:
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300
    
    def get_stock_data(self, symbol: str, period: str = "6mo") -> Optional[pd.DataFrame]:
        # FIXED: Create proper cache key that includes actual fetch period
        fetch_period = self._get_actual_fetch_period(period)
        cache_key = f"{symbol}_{fetch_period}_{period}"
        current_time = time.time()
        
        print(f"🔍 FIXED: Requesting {symbol} for period='{period}' (fetch='{fetch_period}')")
        
        if cache_key in self.cache:
            data, timestamp = self.cache[cache_key]
            if current_time - timestamp < self.cache_timeout:
                print(f"📁 Using cached data for {symbol} ({period})")
                return self._filter_data_for_period(data, period)
        
        try:
            print(f"🌐 FIXED: Fetching {symbol} data - period='{period}', fetch_period='{fetch_period}'")
            ticker = yf.Ticker(symbol)
            
            # Check if symbol exists first
            info = None
            try:
                info = ticker.info
                if not info or 'regularMarketPrice' not in info and 'currentPrice' not in info:
                    print(f"⚠️ {symbol}: possibly delisted; no price data found")
                    return None
            except Exception as e:
                print(f"⚠️ {symbol}: Error getting info - {e}")
            
            # FIXED: Use proper period handling with correct yfinance calls
            if period in ['1d']:
                data = ticker.history(period=period, interval='5m')
                if data.empty:
                    data = ticker.history(period=period)
            elif period in ['5d']:
                data = ticker.history(period=period, interval='1h')
                if data.empty:
                    data = ticker.history(period=period)
            elif period in ['max', '10y', '5y']:
                data = ticker.history(period='max')
                print(f"📊 FIXED: Fetched max data ({len(data)} points), filtering for {period}")
            else:
                data = ticker.history(period=period)
            
            if data is not None and not data.empty:
                if 'Volume' not in data.columns:
                    data['Volume'] = 0
                
                data = data.dropna(subset=['Close'])
                data = data[data['Close'] > 0]
                
                if len(data) > 0:
                    # FIXED: Cache the raw data, filter when needed
                    self.cache[cache_key] = (data.copy(), current_time)
                    
                    # Filter for the requested period
                    filtered_data = self._filter_data_for_period(data, period)
                    
                    print(f"✅ FIXED: Fetched {len(data)} raw points, filtered to {len(filtered_data)} for {symbol} ({period})")
                    return filtered_data
            
            print(f"❌ No data available for {symbol} ({period})")
            return None
            
        except Exception as e:
            print(f"❌ Error fetching {symbol} data: {e}")
            return None
    
    def _get_actual_fetch_period(self, period: str) -> str:
        """FIXED: Get the actual period to fetch from yfinance."""
        if period in ['max', '10y', '5y']:
            return 'max'
        else:
            return period
    
    def _filter_data_for_period(self, data: pd.DataFrame, period: str) -> pd.DataFrame:
        """FIXED: Filter data to the exact requested period."""
        if period == '5y':
            cutoff_date = datetime.now() - timedelta(days=1825)
            filtered = data[data.index >= cutoff_date]
            print(f"🔧 FIXED: Filtered 5y data: {len(data)} -> {len(filtered)} points")
            return filtered
        elif period == '10y':
            cutoff_date = datetime.now() - timedelta(days=3650)
            filtered = data[data.index >= cutoff_date]
            print(f"🔧 FIXED: Filtered 10y data: {len(data)} -> {len(filtered)} points")
            return filtered
        else:
            return data
    
    def get_stock_info(self, symbol: str) -> Dict:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'shares_outstanding': info.get('sharesOutstanding', 0),
                'market_cap': info.get('marketCap', 0),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'company_name': info.get('longName', symbol)
            }
        except:
            return {'shares_outstanding': 0, 'market_cap': 0, 'current_price': None, 'company_name': symbol}
    
    def format_market_cap(self, market_cap: int) -> str:
        if market_cap >= 1_000_000_000_000:
            return f"${market_cap / 1_000_000_000_000:.2f}T"
        elif market_cap >= 1_000_000_000:
            return f"${market_cap / 1_000_000_000:.2f}B"
        elif market_cap >= 1_000_000:
            return f"${market_cap / 1_000_000:.1f}M"
        else:
            return f"${market_cap:,.0f}"
    
    def format_volume(self, volume: int) -> str:
        if volume >= 1_000_000_000:
            return f"{volume / 1_000_000_000:.2f}B"
        elif volume >= 1_000_000:
            return f"{volume / 1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"{volume / 1_000:.1f}K"
        else:
            return f"{volume:,}"

class WidgetFixedRSITracker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ultimate Enhanced RSI Tracker - 🔧 WIDGET FIXED VERSION")
        self.root.geometry("1700x1000")
        self.root.configure(bg='#1e1e1e')
        
        self.stock_data = FixedStockData()
        self.rsi_calculator = RSICalculator()
        
        self.selected_symbol = None
        self.current_canvas = None
        self.chart_frame = None  # FIXED: Explicit chart frame reference
        
        # Watchlist
        self.watchlist = []
        self.watchlist_file = "watchlist.json"
        self.load_watchlist()
        
        # Update control
        self.update_interval = 30
        self.is_updating = False
        self.update_thread = None
        
        self.setup_ui()
        self.setup_styles()
        
        # Start updates
        self.start_updates()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Treeview', 
                       background='#2d2d2d', foreground='white',
                       fieldbackground='#2d2d2d', rowheight=25)
        style.configure('Treeview.Heading',
                       background='#404040', foreground='white',
                       font=('Arial', 9, 'bold'))
        
        style.configure('TNotebook', background='#1e1e1e')
        style.configure('TNotebook.Tab', background='#404040', foreground='white', padding=[20, 8])
        style.map('TNotebook.Tab', background=[('selected', '#00ff88')], foreground=[('selected', 'black')])
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#1e1e1e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, 
                              text="📈 Ultimate Enhanced RSI Tracker - 🔧 WIDGET FIXED VERSION", 
                              font=('Arial', 18, 'bold'),
                              bg='#1e1e1e', fg='#00ff88')
        title_label.pack(pady=(0, 10))
        
        # Create notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.setup_tracker_tab()
        self.setup_charts_tab()
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def setup_tracker_tab(self):
        tracker_frame = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tracker_frame, text="📊 Stock Tracker")
        
        # Controls
        control_frame = tk.Frame(tracker_frame, bg='#1e1e1e')
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Add stock
        add_frame = tk.Frame(control_frame, bg='#1e1e1e')
        add_frame.pack(side=tk.LEFT)
        
        tk.Label(add_frame, text="Add Stock:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.symbol_entry = tk.Entry(add_frame, width=10, font=('Arial', 10))
        self.symbol_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.symbol_entry.bind('<Return>', self.add_stock_event)
        
        tk.Button(add_frame, text="Add", command=self.add_stock,
                 bg='#00ff88', fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = tk.Frame(control_frame, bg='#1e1e1e')
        button_frame.pack(side=tk.RIGHT)
        
        tk.Button(button_frame, text="📈 View Charts", command=self.view_chart,
                 bg='#ff8844', fg='white', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Remove Selected", command=self.remove_stock,
                 bg='#ff4444', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Refresh All", command=self.manual_refresh,
                 bg='#4488ff', fg='white', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Status
        status_frame = tk.Frame(tracker_frame, bg='#1e1e1e')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, text="🔧 WIDGET FIXED VERSION - All features working with market cap analysis!", 
                                    bg='#1e1e1e', fg='#cccccc', font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        self.last_update_label = tk.Label(status_frame, text="", 
                                         bg='#1e1e1e', fg='#888888', font=('Arial', 9))
        self.last_update_label.pack(side=tk.RIGHT)
        
        # Table
        self.setup_table(tracker_frame)
        
        # Legend
        self.setup_legend(tracker_frame)
    
    def setup_charts_tab(self):
        charts_frame = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(charts_frame, text="📈 WIDGET FIXED Charts")
        
        # Chart controls
        chart_control_frame = tk.Frame(charts_frame, bg='#1e1e1e')
        chart_control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Symbol selection
        tk.Label(chart_control_frame, text="Stock Symbol:", 
                bg='#1e1e1e', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        self.chart_symbol_var = tk.StringVar()
        self.chart_symbol_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_symbol_var, 
                                              width=8, font=('Arial', 11))
        self.chart_symbol_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        # Period selection  
        tk.Label(chart_control_frame, text="Period:", 
                bg='#1e1e1e', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.LEFT)
        
        self.chart_period_var = tk.StringVar(value="6mo")
        self.period_combo = ttk.Combobox(chart_control_frame, textvariable=self.chart_period_var, 
                                        values=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max"], 
                                        width=8, font=('Arial', 11))
        self.period_combo.pack(side=tk.LEFT, padx=(5, 15))
        
        # FIXED: Improved event binding
        self.period_combo.bind('<<ComboboxSelected>>', self.on_period_changed_WIDGET_FIXED)
        
        # Load button
        tk.Button(chart_control_frame, text="📊 Load Chart", command=self.load_chart_WIDGET_FIXED,
                 bg='#00ff88', fg='black', font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Clear cache button
        tk.Button(chart_control_frame, text="🗑️ Clear Cache", command=self.clear_cache_and_reload,
                 bg='#ff4488', fg='white', font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Debug info
        debug_frame = tk.Frame(chart_control_frame, bg='#1e1e1e')
        debug_frame.pack(side=tk.RIGHT)
        
        self.debug_label = tk.Label(debug_frame, text="Ready", 
                                   bg='#1e1e1e', fg='#888888', font=('Arial', 9))
        self.debug_label.pack()
        
        # FIXED: Chart display with proper frame management
        self.chart_frame = tk.Frame(charts_frame, bg='#1e1e1e')
        self.chart_frame.pack(fill=tk.BOTH, expand=True)
        
        # Initial message
        self.show_initial_message()
    
    def show_initial_message(self):
        """FIXED: Safely show initial message"""
        try:
            # Clear any existing widgets safely
            self.clear_chart_safely()
            
            initial_text = "🔧 WIDGET FIXED VERSION with MARKET CAP!\n\n✅ FIXED: Tkinter widget destruction\n✅ FIXED: Chart loading after first use\n✅ FIXED: Multiple symbol/period switching\n📊 ADDED: Market Cap Analysis Chart\n\n🎯 Add stocks, then switch between symbols/periods freely!\n💰 Market cap trends and moving averages included!"
            
            self.chart_message = tk.Label(self.chart_frame, text=initial_text,
                                         bg='#1e1e1e', fg='#cccccc', font=('Arial', 12))
            self.chart_message.pack(expand=True)
        except Exception as e:
            print(f"❌ Error showing initial message: {e}")
    
    def clear_chart_safely(self):
        """FIXED: Safely clear chart without breaking widget references"""
        try:
            # Destroy current canvas if it exists
            if self.current_canvas:
                self.current_canvas.get_tk_widget().destroy()
                self.current_canvas = None
            
            # Clear all widgets in chart frame safely
            if self.chart_frame and self.chart_frame.winfo_exists():
                for widget in self.chart_frame.winfo_children():
                    try:
                        widget.destroy()
                    except tk.TclError:
                        pass  # Widget already destroyed
        except Exception as e:
            print(f"⚠️ Warning during chart clearing: {e}")
    
    def on_period_changed_WIDGET_FIXED(self, event=None):
        """FIXED: Enhanced period change handler with widget safety."""
        try:
            symbol = self.chart_symbol_var.get().strip().upper()
            period = self.chart_period_var.get()
            
            print(f"🔧 WIDGET FIXED: Period dropdown changed to '{period}' for symbol '{symbol}'")
            
            if not symbol:
                self.debug_label.config(text=f"Period: {period} (no symbol)")
                return
            
            # Update debug info safely
            if self.debug_label.winfo_exists():
                self.debug_label.config(text=f"Loading: {symbol} ({period})")
            
            if self.status_label.winfo_exists():
                self.status_label.config(text=f"🔧 Auto-loading {symbol} for period '{period}'...")
            
            self.root.update()
            
            # FIXED: Load with delay to prevent widget conflicts
            self.root.after(200, self.load_chart_WIDGET_FIXED)
            
        except Exception as e:
            print(f"❌ Error in period change handler: {e}")
    
    def load_chart_WIDGET_FIXED(self):
        """FIXED: Load chart with proper widget management."""
        try:
            if not CHARTS_AVAILABLE:
                messagebox.showwarning("Charts Not Available", "Install matplotlib: pip install matplotlib")
                return
            
            symbol = self.chart_symbol_var.get().strip().upper()
            if not symbol:
                messagebox.showwarning("No Symbol", "Please select a stock symbol")
                return
            
            period = self.chart_period_var.get()
            
            print(f"🔧 WIDGET FIXED: Loading chart for symbol='{symbol}', period='{period}'")
            
            # Update debug display safely
            if self.debug_label and self.debug_label.winfo_exists():
                self.debug_label.config(text=f"Fetching: {symbol} ({period})")
            
            # FIXED: Clear chart safely before loading new one
            self.clear_chart_safely()
            
            # Show loading message
            loading_text = f"🔧 WIDGET FIXED: Loading {symbol} chart for period '{period}'...\nFetching data..."
            loading_label = tk.Label(self.chart_frame, text=loading_text,
                                   bg='#1e1e1e', fg='#cccccc', font=('Arial', 12))
            loading_label.pack(expand=True)
            self.root.update()
            
            # FIXED: Fetch data with enhanced error handling
            print(f"🌐 WIDGET FIXED: Calling get_stock_data('{symbol}', '{period}')")
            data = self.stock_data.get_stock_data(symbol, period)
            
            if data is None or data.empty:
                error_msg = f"No data available for {symbol} (period: {period})\nSymbol may be delisted or invalid."
                print(f"❌ {error_msg}")
                
                # Clear loading message
                loading_label.destroy()
                
                # Show error message
                error_label = tk.Label(self.chart_frame, text=error_msg,
                                     bg='#1e1e1e', fg='#ff4444', font=('Arial', 12))
                error_label.pack(expand=True)
                
                if self.debug_label and self.debug_label.winfo_exists():
                    self.debug_label.config(text="Error: No data")
                return
            
            # Get stock info
            stock_info = self.stock_data.get_stock_info(symbol)
            
            # Clear loading message
            loading_label.destroy()
            
            # FIXED: Create chart with safe widget management
            print(f"✅ WIDGET FIXED: Creating chart with {len(data)} data points for {symbol} ({period})")
            self.create_complete_chart_WIDGET_FIXED(symbol, data, period, stock_info)
            
            # Update status with verification
            data_start = data.index[0].strftime('%Y-%m-%d')
            data_end = data.index[-1].strftime('%Y-%m-%d')
            data_span = (data.index[-1] - data.index[0]).days
            
            status_msg = f"✅ WIDGET FIXED: {symbol} ({period}) - {len(data)} points, {data_span} days"
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=status_msg)
            
            if self.debug_label and self.debug_label.winfo_exists():
                self.debug_label.config(text=f"✅ {symbol} ({period}) - {len(data)} pts")
            
            print(f"✅ WIDGET FIXED: Chart loaded successfully!")
            
        except Exception as e:
            error_msg = f"❌ WIDGET FIXED: Error loading chart: {e}"
            print(error_msg)
            
            # Clear any widgets safely
            self.clear_chart_safely()
            
            # Show error
            error_label = tk.Label(self.chart_frame, text=f"Error loading chart:\n{str(e)}",
                                 bg='#1e1e1e', fg='#ff4444', font=('Arial', 12))
            error_label.pack(expand=True)
            
            if self.debug_label and self.debug_label.winfo_exists():
                self.debug_label.config(text="Error occurred")
    
    def create_complete_chart_WIDGET_FIXED(self, symbol: str, data: pd.DataFrame, period: str, stock_info: Dict):
        """FIXED: Create chart with safe widget management and market cap analysis."""
        try:
            # Create figure with 4 subplots including market cap
            fig = Figure(figsize=(15, 12), facecolor='#1e1e1e')
            
            # Data verification
            data_span_days = (data.index[-1] - data.index[0]).days
            data_start = data.index[0].strftime('%Y-%m-%d')
            data_end = data.index[-1].strftime('%Y-%m-%d')
            
            print(f"📊 WIDGET FIXED: Chart data spans {data_span_days} days ({data_start} to {data_end})")
            
            # 1. PRICE CHART
            ax1 = fig.add_subplot(411, facecolor='#2d2d2d')
            ax1.plot(data.index, data['Close'], color='#00ff88', linewidth=2.5, label='Price')
            
            # Moving averages
            if len(data) >= 20:
                ma20 = data['Close'].rolling(window=20).mean()
                ax1.plot(data.index, ma20, color='#ffaa00', linewidth=1.5, alpha=0.8, label='MA20')
            if len(data) >= 50:
                ma50 = data['Close'].rolling(window=50).mean()
                ax1.plot(data.index, ma50, color='#ff4444', linewidth=1.5, alpha=0.8, label='MA50')
            
            # FIXED: Enhanced title with verification
            verified_title = f'✅ {symbol} - WIDGET FIXED (PERIOD: {period}) - {len(data)} points | {data_start} to {data_end}'
            ax1.set_title(verified_title, color='white', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Price ($)', color='white')
            ax1.legend(loc='upper left')
            ax1.grid(True, alpha=0.3, color='white')
            ax1.tick_params(colors='white')
            
            # 2. RSI CHART
            ax2 = fig.add_subplot(412, facecolor='#2d2d2d')
            rsi_data = self.rsi_calculator.calculate_rsi(data['Close'])
            current_rsi = rsi_data.iloc[-1]
            
            ax2.plot(data.index, rsi_data, color='#4488ff', linewidth=2.5, label='RSI')
            ax2.axhline(y=70, color='#ff4444', linestyle='--', alpha=0.8, label='Overbought (70)')
            ax2.axhline(y=30, color='#44ff44', linestyle='--', alpha=0.8, label='Oversold (30)')
            ax2.axhline(y=50, color='#888888', linestyle='-', alpha=0.6, label='Neutral (50)')
            
            # RSI zones
            ax2.fill_between(data.index, 70, 100, alpha=0.1, color='red')
            ax2.fill_between(data.index, 0, 30, alpha=0.1, color='green')
            
            rsi_status = "Overbought" if current_rsi > 70 else "Oversold" if current_rsi < 30 else "Neutral"
            rsi_color = "#ff4444" if current_rsi > 70 else "#44ff44" if current_rsi < 30 else "#ffaa00"
            
            ax2.set_title(f'RSI (14-period) - Current: {current_rsi:.1f} ({rsi_status})', 
                         color=rsi_color, fontsize=12, fontweight='bold')
            ax2.set_ylabel('RSI', color='white')
            ax2.set_ylim(0, 100)
            ax2.legend(loc='upper left')
            ax2.grid(True, alpha=0.3, color='white')
            ax2.tick_params(colors='white')
            
            # 3. VOLUME CHART
            ax3 = fig.add_subplot(413, facecolor='#2d2d2d')
            
            # Color volume bars
            volume_colors = []
            for i in range(len(data)):
                if i == 0:
                    volume_colors.append('#888888')
                else:
                    if data['Close'].iloc[i] >= data['Close'].iloc[i-1]:
                        volume_colors.append('#44ff44')
                    else:
                        volume_colors.append('#ff4444')
            
            ax3.bar(data.index, data['Volume'], color=volume_colors, alpha=0.7)
            
            # Average volume
            avg_vol = data['Volume'].mean()
            if avg_vol > 0:
                ax3.axhline(y=avg_vol, color='#ffaa00', linewidth=2, 
                           label=f'Avg Vol: {self.stock_data.format_volume(int(avg_vol))}')
            
            current_vol = int(data['Volume'].iloc[-1])
            vol_vs_avg = (current_vol / avg_vol - 1) * 100 if avg_vol > 0 else 0
            vol_status = f"+{vol_vs_avg:.0f}%" if vol_vs_avg > 0 else f"{vol_vs_avg:.0f}%"
            
            ax3.set_title(f'Volume - Current: {self.stock_data.format_volume(current_vol)} ({vol_status} vs avg)', 
                         color='white', fontsize=12, fontweight='bold')
            ax3.set_ylabel('Volume', color='white')
            ax3.legend(loc='upper left')
            ax3.grid(True, alpha=0.3, color='white')
            ax3.tick_params(colors='white')
            
            # 4. MARKET CAP CHART
            ax4 = fig.add_subplot(414, facecolor='#2d2d2d')
            
            shares_outstanding = stock_info.get('shares_outstanding', 0)
            if shares_outstanding > 0:
                # Market cap over time
                market_cap_series = data['Close'] * shares_outstanding
                ax4.plot(data.index, market_cap_series, color='#ff8844', linewidth=2.5, label='Market Cap')
                ax4.fill_between(data.index, market_cap_series, alpha=0.2, color='#ff8844')
                
                # Market cap moving average
                if len(data) >= 20:
                    mc_ma = market_cap_series.rolling(window=20).mean()
                    ax4.plot(data.index, mc_ma, color='#ffaa00', linewidth=1.5, alpha=0.8, label='MC MA20')
                
                current_mc = market_cap_series.iloc[-1]
                ax4.set_title(f'Market Cap Trend - Current: {self.stock_data.format_market_cap(int(current_mc))}', 
                             color='white', fontsize=12, fontweight='bold')
                ax4.set_ylabel('Market Cap ($)', color='white')
                ax4.yaxis.set_major_formatter(plt.FuncFormatter(self._format_market_cap_axis))
            else:
                # Price performance fallback
                normalized_price = (data['Close'] / data['Close'].iloc[0]) * 100
                ax4.plot(data.index, normalized_price, color='#8844ff', linewidth=2.5, label='Price Performance %')
                ax4.axhline(y=100, color='#888888', linestyle='-', alpha=0.5, label='Baseline')
                
                current_perf = normalized_price.iloc[-1] - 100
                perf_status = f"+{current_perf:.1f}%" if current_perf >= 0 else f"{current_perf:.1f}%"
                ax4.set_title(f'Price Performance - {perf_status} vs start', 
                             color='white', fontsize=12, fontweight='bold')
                ax4.set_ylabel('Performance (%)', color='white')
            
            ax4.set_xlabel('Date', color='white')
            ax4.legend(loc='upper left')
            ax4.grid(True, alpha=0.3, color='white')
            ax4.tick_params(colors='white')
            
            # Smart date formatting
            if data_span_days > 365 * 2:
                date_format = '%Y'
            elif data_span_days > 90:
                date_format = '%m/%y'
            else:
                date_format = '%m/%d'
            
            for ax in [ax1, ax2, ax3, ax4]:
                ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            
            fig.autofmt_xdate(rotation=45)
            fig.tight_layout(pad=2.0)
            
            # FIXED: Embed in tkinter with safe widget management
            self.current_canvas = FigureCanvasTkAgg(fig, self.chart_frame)
            self.current_canvas.draw()
            self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            print(f"✅ WIDGET FIXED: Chart embedded successfully")
            
        except Exception as e:
            print(f"❌ Error creating chart: {e}")
            raise
    
    def _format_market_cap_axis(self, x, p):
        """Format market cap axis values."""
        if x >= 1_000_000_000_000:
            return f'${x/1_000_000_000_000:.1f}T'
        elif x >= 1_000_000_000:
            return f'${x/1_000_000_000:.1f}B'
        elif x >= 1_000_000:
            return f'${x/1_000_000:.1f}M'
        else:
            return f'${x:,.0f}'
    
    def clear_cache_and_reload(self):
        """Clear cache and reload with fresh data."""
        try:
            symbol = self.chart_symbol_var.get().strip().upper()
            period = self.chart_period_var.get()
            
            if not symbol:
                messagebox.showwarning("No Symbol", "Please select a stock symbol first")
                return
            
            print(f"🗑️ WIDGET FIXED: Clearing cache for all {symbol} data")
            
            # Clear all cache entries for this symbol
            keys_to_remove = [key for key in self.stock_data.cache.keys() if key.startswith(f"{symbol}_")]
            for key in keys_to_remove:
                del self.stock_data.cache[key]
                print(f"🗑️ Removed cache key: {key}")
            
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=f"🗑️ Cache cleared for {symbol}, loading fresh {period} data...")
            if self.debug_label and self.debug_label.winfo_exists():
                self.debug_label.config(text="Fresh data loading...")
            
            self.root.update()
            time.sleep(0.3)
            self.load_chart_WIDGET_FIXED()
            
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
    
    # Simplified tracker functionality (keeping core features)
    def setup_table(self, parent):
        table_frame = tk.Frame(parent, bg='#1e1e1e')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Symbol', 'Price', 'Change', 'Change%', 'RSI', 'Status', 'Updated')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        headings = {
            'Symbol': ('Stock', 70), 'Price': ('Price ($)', 80), 'Change': ('Change ($)', 80), 
            'Change%': ('Change %', 80), 'RSI': ('RSI', 60), 'Status': ('RSI Status', 100),
            'Updated': ('Updated', 80)
        }
        
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_stock_select)
    
    def setup_legend(self, parent):
        legend_frame = tk.Frame(parent, bg='#1e1e1e')
        legend_frame.pack(pady=10)
        
        tk.Label(legend_frame, text="🔧 WIDGET FIXED FEATURES:", 
                bg='#1e1e1e', fg='white', font=('Arial', 10, 'bold')).pack()
        
        features = "✅ Widget Destruction FIXED  ✅ Multiple Chart Loading FIXED  ✅ Symbol Switching FIXED  ✅ Market Cap Analysis"
        tk.Label(legend_frame, text=features,
                bg='#1e1e1e', fg='#00ff88', font=('Arial', 9, 'bold')).pack()
        
        rsi_legend = "🔴 Overbought (>70)  🟡 Neutral (30-70)  🟢 Oversold (<30)"
        tk.Label(legend_frame, text=rsi_legend,
                bg='#1e1e1e', fg='#888888', font=('Arial', 9)).pack()
    
    # Essential methods for functionality
    def on_stock_select(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_symbol = selected[0]
            self.chart_symbol_var.set(self.selected_symbol)
            self.chart_symbol_combo['values'] = self.watchlist
    
    def on_tab_changed(self, event):
        if "Charts" in event.widget.tab(event.widget.select(), "text"):
            self.chart_symbol_combo['values'] = self.watchlist
            if self.selected_symbol:
                self.chart_symbol_var.set(self.selected_symbol)
    
    def view_chart(self):
        if not CHARTS_AVAILABLE:
            messagebox.showwarning("Charts Not Available", "Install matplotlib: pip install matplotlib")
            return
            
        if not self.selected_symbol:
            messagebox.showwarning("No Selection", "Please select a stock")
            return
        
        self.notebook.select(1)
        self.chart_symbol_var.set(self.selected_symbol)
        self.load_chart_WIDGET_FIXED()
    
    def add_stock_event(self, event):
        self.add_stock()
    
    def add_stock(self):
        symbol = self.symbol_entry.get().strip().upper()
        if not symbol:
            return
        
        if symbol in self.watchlist:
            messagebox.showwarning("Duplicate", f"{symbol} already in watchlist!")
            return
        
        # Quick validation
        data = self.stock_data.get_stock_data(symbol, "5d")
        if data is None or data.empty:
            messagebox.showerror("Invalid Symbol", f"Could not find data for {symbol}")
            return
        
        self.watchlist.append(symbol)
        self.symbol_entry.delete(0, tk.END)
        self.save_watchlist()
        
        loading_values = (symbol, "Loading...", "", "", "", "", "")
        self.tree.insert('', tk.END, iid=symbol, values=loading_values)
        
        # Quick update
        threading.Thread(target=self.update_stock_data, args=(symbol,), daemon=True).start()
        if self.status_label and self.status_label.winfo_exists():
            self.status_label.config(text=f"Added {symbol}")
    
    def remove_stock(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a stock")
            return
        
        symbol = selected[0]
        if messagebox.askyesno("Confirm Remove", f"Remove {symbol}?"):
            self.watchlist.remove(symbol)
            self.tree.delete(symbol)
            self.save_watchlist()
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text=f"Removed {symbol}")
    
    def manual_refresh(self):
        if not self.watchlist:
            messagebox.showinfo("Empty Watchlist", "Add some stocks first!")
            return
        
        if self.status_label and self.status_label.winfo_exists():
            self.status_label.config(text="Refreshing all stocks...")
        threading.Thread(target=self.refresh_all_stocks, daemon=True).start()
    
    def refresh_all_stocks(self):
        for symbol in self.watchlist:
            self.update_stock_data(symbol)
            time.sleep(0.5)
        
        if self.status_label and self.status_label.winfo_exists():
            self.root.after(0, lambda: self.status_label.config(text="All stocks updated"))
    
    def update_stock_data(self, symbol: str):
        try:
            hist_data = self.stock_data.get_stock_data(symbol, "1mo")
            stock_info = self.stock_data.get_stock_info(symbol)
            
            if hist_data is None or hist_data.empty:
                error_values = (symbol, "Error", "N/A", "N/A", "N/A", "N/A", "Error")
                self.root.after(0, lambda: self.update_table_row(symbol, *error_values))
                return
            
            current_price = stock_info['current_price']
            if current_price is None:
                current_price = float(hist_data['Close'].iloc[-1])
            
            previous_price = float(hist_data['Close'].iloc[-2]) if len(hist_data) > 1 else current_price
            price_change = current_price - previous_price
            percent_change = (price_change / previous_price) * 100 if previous_price != 0 else 0
            
            rsi_series = self.rsi_calculator.calculate_rsi(hist_data['Close'])
            rsi = float(rsi_series.iloc[-1])
            
            if rsi > 70:
                rsi_status = "🔴 Overbought"
            elif rsi < 30:
                rsi_status = "🟢 Oversold"
            else:
                rsi_status = "🟡 Neutral"
            
            values = (
                symbol,
                f"${current_price:.2f}",
                f"${price_change:+.2f}",
                f"{percent_change:+.2f}%",
                f"{rsi:.1f}",
                rsi_status,
                datetime.now().strftime("%H:%M:%S")
            )
            
            self.root.after(0, lambda: self.update_table_row(symbol, *values))
            
        except Exception as e:
            print(f"Error updating {symbol}: {e}")
            error_values = (symbol, "Error", "N/A", "N/A", "N/A", "N/A", "Error")
            self.root.after(0, lambda: self.update_table_row(symbol, *error_values))
    
    def update_table_row(self, symbol: str, *values):
        try:
            if self.tree.exists(symbol):
                self.tree.item(symbol, values=values)
        except tk.TclError:
            pass
    
    def start_updates(self):
        if not self.is_updating:
            self.is_updating = True
            self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
            self.update_thread.start()
    
    def update_loop(self):
        while self.is_updating:
            if self.watchlist:
                for symbol in self.watchlist.copy():
                    if not self.is_updating:
                        break
                    self.update_stock_data(symbol)
                    time.sleep(2)
                
                current_time = datetime.now().strftime("%H:%M:%S")
                if self.last_update_label and self.last_update_label.winfo_exists():
                    self.root.after(0, lambda: self.last_update_label.config(text=f"Last: {current_time}"))
            
            time.sleep(self.update_interval)
    
    def load_watchlist(self):
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    self.watchlist = json.load(f)
        except:
            self.watchlist = ["AAPL", "TSLA", "MSFT", "GOOGL", "NVDA"]  # Default stocks
    
    def save_watchlist(self):
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watchlist, f)
        except:
            pass
    
    def populate_initial_data(self):
        for symbol in self.watchlist:
            loading_values = (symbol, "Loading...", "", "", "", "", "")
            self.tree.insert('', tk.END, iid=symbol, values=loading_values)
    
    def on_closing(self):
        self.is_updating = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        self.root.destroy()
    
    def run(self):
        self.populate_initial_data()
        
        if not self.watchlist:
            if self.status_label and self.status_label.winfo_exists():
                self.status_label.config(text="🔧 WIDGET FIXED VERSION! Add stocks to test multiple chart loading.")
        
        print("🚀 Starting WIDGET FIXED Ultimate RSI Tracker with Market Cap Analysis...")
        print("🔧 WIDGET FIXED VERSION with MARKET CAP ACTIVE!")
        print("✅ FIXED: Tkinter widget destruction bug")
        print("✅ FIXED: Chart loading after first use")
        print("✅ FIXED: Multiple symbol/period switching")
        print("📊 ADDED: Market Cap Analysis with trends and moving averages")
        print("💰 4 Complete Charts: Price, RSI, Volume, Market Cap")
        print("")
        
        self.root.mainloop()

def main():
    try:
        app = WidgetFixedRSITracker()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        messagebox.showerror("Error", f"Failed to start: {e}")

if __name__ == "__main__":
    main()
