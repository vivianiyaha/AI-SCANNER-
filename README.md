# 📡 AI SCANNER — SMC/ICT Automated Signal Dashboard

**Emevine AI Trading System**  
Full SMC · ICT · Price Action · Multi-Timeframe Analysis

---

## 🚀 Quick Start

### 1. Install Python 3.10+
Download from https://python.org

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the app
```bash
streamlit run app.py
```

The dashboard will open automatically at **http://localhost:8501**

---

## 📋 Features

### 🎯 Signal Engine
- Full SMC/ICT analysis: BOS, CHOCH, Order Blocks, FVG, Liquidity Sweeps
- AI weighted confidence scoring (only signals ≥75% are shown)
- Entry, Stop Loss, TP1/TP2/TP3, Risk:Reward for every signal
- Detailed trade reason per signal
- Multi-timeframe support (M1 to D1)

### 📊 Markets Supported
| Category | Pairs |
|----------|-------|
| **Forex** | EUR/USD, USD/CHF, GBP/USD, USD/JPY, AUD/USD |
| **Crypto** | ETH/USD, LTC/USD, XRP/USD, BCH/USD |
| **Synthetics** | Boom 500/1000, Crash 500/1000, Volatility 10/25/50/75/100 |

### 🤖 AI Scoring Weights
| Factor | Weight |
|--------|--------|
| Market Structure (HH/HL/LH/LL + BOS/CHOCH) | 25% |
| SMC Confirmation (OB + FVG) | 25% |
| RSI Confirmation | 15% |
| EMA Trend (50 / 200) | 15% |
| Liquidity Sweep | 10% |
| Price Action (Pin Bar / Engulfing) | 10% |

### 💼 Risk Management
- Position size auto-calculated: `(Balance × Risk%) / SL distance`
- Daily loss limit with auto halt
- Daily profit target
- Max open trades per session
- Per-pair duplicate prevention

### 📁 Storage
- **SQLite DB** (`ai_scanner.db`): signals, trades, account_history, daily_summary
- **CSV log** (`trade_log.csv`): timestamped activity log
- Export buttons on every table tab

---

## 🛠 Configuration (Sidebar)

| Setting | Description |
|---------|-------------|
| Account Type | Filter pairs by category |
| Select Pairs | Choose which pairs to scan |
| Timeframe | Candle resolution |
| Account Balance | Your starting balance |
| Risk Per Trade | % of balance to risk |
| Max Lot Size | Upper cap on position size |
| Daily Loss Limit | Auto-halt threshold |
| Daily Profit Target | Session goal |
| Max Open Trades | Concurrent position cap |
| Scan Interval | Seconds between scans (30–300) |

---

## ▶️ Bot Controls

| Button | Action |
|--------|--------|
| **START** | Begin continuous scanning |
| **STOP** | Pause scanning |
| **Close All Trades** | Force-close all open positions |
| **Reset Session** | Clear trades/signals/logs |
| **Run Manual Scan** | One-off scan (Signals tab) |

---

## 📡 Auto-Scan Behaviour

When START is clicked:
1. Scans all selected pairs every N seconds (your scan interval)
2. Runs full SMC/ICT analysis on each pair
3. Signals with ≥75% confidence are displayed and logged
4. Qualifying signals automatically open simulated trades
5. Open trades are checked each cycle for SL/TP hits
6. If daily loss limit is reached, all scanning halts automatically
7. The page auto-reruns to continue scanning — keep the browser tab open

> **Note:** For real continuous running even with tab closed, deploy to Streamlit Cloud or a VPS with `nohup streamlit run app.py &`

---

## 🌐 Data Sources

- **Forex & Crypto**: Yahoo Finance via `yfinance` (real market data)
- **Synthetics**: Proprietary synthetic OHLCV generator with realistic price behavior
- Falls back to synthetic data if yfinance is unavailable

---

## ⚠️ Risk Warning

This software is for **educational and research purposes only**. Trading financial instruments carries significant risk of loss. Past performance does not guarantee future results. Always use proper risk management and consult a qualified financial advisor before trading real funds.

---

## 📂 File Structure

```
ai_scanner/
├── app.py                  ← Main application
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
├── .streamlit/
│   └── config.toml         ← Theme configuration
├── ai_scanner.db           ← SQLite database (auto-created)
└── trade_log.csv           ← CSV log (auto-created)
```
