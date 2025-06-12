# 🚀 Ultimate Enhanced RSI Stock Tracker

**Professional Stock Analysis Dashboard with Market Cap Analysis**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](README.md)

## 📊 **Features Overview**

### **4 Comprehensive Chart Panels:**
- 📈 **Price Chart** - Stock price with MA20/MA50 moving averages
- 📊 **RSI Analysis** - 14-period RSI with overbought/oversold zones
- 📊 **Volume Analysis** - Volume bars with color coding and average lines
- 💰 **Market Cap Analysis** - Market capitalization trends and moving averages

### **Professional Trading Interface:**
- ✅ **Real-time Data** - Live stock data via yfinance API
- ✅ **Multiple Timeframes** - 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max
- ✅ **Portfolio Management** - Add/remove stocks, import CSV portfolios
- ✅ **Dark Theme** - Professional dark interface for trading
- ✅ **Auto-refresh** - Automatic data updates every 30 seconds
- ✅ **Smart Caching** - Efficient data caching for faster performance

### **Technical Indicators:**
- 🔴 **RSI Overbought** (>70) - Potential sell signals
- 🟢 **RSI Oversold** (<30) - Potential buy signals
- 🟡 **RSI Neutral** (30-70) - Balanced conditions
- 📊 **Volume Analysis** - Current vs average volume comparison
- 💰 **Market Cap Trends** - Company valuation analysis

## 🎯 **Quick Start**

### **Installation:**

```bash
# Clone the repository
git clone https://github.com/Benggoy/ultimate-rsi-tracker.git
cd ultimate-rsi-tracker

# Install requirements
pip install -r requirements.txt

# Run the application
python ultimate_rsi_tracker.py
```

### **Requirements:**
- Python 3.8+
- tkinter (included with Python)
- yfinance, pandas, matplotlib, numpy
- Internet connection for real-time data

## 📱 **Usage Guide**

### **Getting Started:**
1. **Launch the application** - Run `python ultimate_rsi_tracker.py`
2. **Add stocks** - Enter symbol (e.g., AAPL) and click "Add"
3. **View charts** - Select stock and go to "Charts" tab
4. **Change timeframes** - Use dropdown to select period (1d to max)
5. **Analyze data** - Review all 4 chart panels for comprehensive analysis

### **Chart Navigation:**
- **Price Panel** - Stock price trends with moving averages
- **RSI Panel** - Momentum indicator for buy/sell signals
- **Volume Panel** - Trading activity analysis
- **Market Cap Panel** - Company valuation trends

### **Key Controls:**
- **Load Chart** - Refresh data and display charts
- **Clear Cache** - Force fresh data fetch
- **Period Dropdown** - Select timeframe (auto-updates charts)
- **Symbol Dropdown** - Switch between tracked stocks

## 🔧 **Technical Features**

### **Advanced Fixes Applied:**
- ✅ **Widget Destruction Fix** - Prevents tkinter crashes after chart loads
- ✅ **Period Synchronization** - Ensures dropdown matches displayed data
- ✅ **Enhanced Caching** - Smart cache keys for different periods
- ✅ **Error Handling** - Graceful handling of delisted/invalid stocks
- ✅ **Memory Management** - Proper widget cleanup and memory usage

### **Data Pipeline:**
- **yfinance Integration** - Real-time stock data fetching
- **Pandas Processing** - Efficient data manipulation and analysis
- **Matplotlib Rendering** - Professional chart generation
- **Smart Filtering** - Accurate period-based data filtering

## 📊 **Chart Analysis**

### **RSI Indicator (Relative Strength Index):**
- **Purpose:** Measures momentum and identifies overbought/oversold conditions
- **Range:** 0-100 scale
- **Signals:**
  - RSI > 70: Potentially overbought (consider selling)
  - RSI < 30: Potentially oversold (consider buying)
  - RSI 30-70: Neutral territory

### **Moving Averages:**
- **MA20:** 20-day moving average (short-term trend)
- **MA50:** 50-day moving average (medium-term trend)
- **Usage:** Price above MA = uptrend, below MA = downtrend

### **Volume Analysis:**
- **Green bars:** Higher volume on up days
- **Red bars:** Higher volume on down days
- **Average line:** Compares current volume to historical average

### **Market Cap Analysis:**
- **Purpose:** Shows company valuation trends over time
- **Calculation:** Stock Price × Shares Outstanding
- **Trends:** Helps identify growth vs value opportunities

## 💼 **Portfolio Management**

### **Adding Stocks:**
1. Enter stock symbol in the input field
2. Click "Add" or press Enter
3. Stock will be validated and added to watchlist
4. Data will automatically start updating

### **Import Portfolio:**
- Click "📁 Import Portfolio" button
- Select CSV file with stock symbols
- Supported formats: CSV with 'Symbol' column or plain text list
- All valid symbols will be imported automatically

## 🖥️ **Platform Support**

### **Cross-Platform Compatibility:**
- ✅ **Windows** - Full support with native look
- ✅ **macOS** - Native macOS interface
- ✅ **Linux** - Complete functionality on all distributions

### **macOS App Creation:**
Create a Mac app for the Dock:
```bash
# Using Automator (manual)
# 1. Open Automator → Application
# 2. Add "Run Shell Script"
# 3. Paste: cd "/path/to/app" && python3 ultimate_rsi_tracker.py
# 4. Save as "RSI Tracker.app"
```

## 🚨 **Troubleshooting**

### **Common Issues:**

**Charts not loading:**
```bash
pip install matplotlib
# Restart the application
```

**No data for symbol:**
- Verify symbol is correct (e.g., AAPL not Apple)
- Check if symbol is delisted
- Try different time period

**App crashes on chart switching:**
- This version includes widget destruction fixes
- If issues persist, restart the application

## 📈 **Investment Strategies**

- **Value Investing:** Focus on low RSI + strong fundamentals
- **Growth Investing:** Monitor market cap trends and momentum
- **Technical Analysis:** Use RSI + volume for entry/exit points
- **Risk Management:** Set alerts based on RSI extremes

## 🔒 **Data & Privacy**

- **No Personal Data:** App only processes public stock data
- **Local Storage:** All data cached locally, no cloud uploads
- **API Usage:** Uses yfinance (Yahoo Finance) public API
- **Offline Mode:** Cached data available without internet

## 🤝 **Contributing**

Contributions welcome! Areas for enhancement:
- Additional technical indicators (MACD, Bollinger Bands)
- Real-time streaming data
- Alert system for RSI thresholds
- Export functionality for charts

## 📄 **License**

MIT License - see LICENSE file for details.

## 🙏 **Acknowledgments**

- **yfinance** - Yahoo Finance API wrapper
- **matplotlib** - Professional charting library
- **pandas** - Data analysis framework
- **tkinter** - Cross-platform GUI framework

---

**🚀 Ready to start professional stock analysis? Clone the repo and launch your trading dashboard!**

📊 **Happy Trading!** 💰