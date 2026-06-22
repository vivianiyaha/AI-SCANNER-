"""
AI SCANNER - SMC/ICT Automated Signal & Trading Dashboard
Author: Emevine AI Scanner
Color scheme: White, Black, Green, Burnt Orange
"""

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import time
import threading
import logging
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

# ── Optional imports ──────────────────────────────────────────────────────────
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI SCANNER",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import fonts */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global reset & palette */
:root {
    --bg:          #0a0a0a;
    --surface:     #111111;
    --surface2:    #1a1a1a;
    --border:      #222222;
    --orange:      #cc5500;
    --orange-lt:   #e06020;
    --green:       #00c853;
    --green-dk:    #00903c;
    --red:         #e53935;
    --white:       #f0f0f0;
    --muted:       #666666;
    --font:        'Space Grotesk', sans-serif;
    --mono:        'JetBrains Mono', monospace;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--white) !important;
    font-family: var(--font) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--white) !important; }

/* Headers */
h1 { color: var(--orange) !important; font-size: 2rem !important; letter-spacing: -0.5px; }
h2 { color: var(--white) !important; border-bottom: 1px solid var(--border); padding-bottom: 6px; }
h3 { color: var(--orange-lt) !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 12px 16px !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
[data-testid="stMetricValue"] { color: var(--white) !important; font-family: var(--mono) !important; }
[data-testid="stMetricDelta"] { font-family: var(--mono) !important; }

/* Buttons */
.stButton > button {
    background: transparent !important;
    border: 1px solid var(--orange) !important;
    color: var(--orange) !important;
    border-radius: 4px !important;
    font-family: var(--font) !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
    padding: 8px 20px !important;
}
.stButton > button:hover {
    background: var(--orange) !important;
    color: #000 !important;
}

/* Primary action buttons */
.btn-start button { border-color: var(--green) !important; color: var(--green) !important; }
.btn-start button:hover { background: var(--green) !important; color: #000 !important; }
.btn-stop button { border-color: var(--red) !important; color: var(--red) !important; }
.btn-stop button:hover { background: var(--red) !important; color: #fff !important; }

/* DataFrames */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 8px; overflow: hidden; }
.stDataFrame th { background: var(--surface2) !important; color: var(--orange) !important; font-size: 0.7rem !important; text-transform: uppercase; letter-spacing: 1px; }
.stDataFrame td { color: var(--white) !important; font-family: var(--mono) !important; font-size: 0.8rem !important; }

/* Expander */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Select / Input */
.stSelectbox > div > div, .stNumberInput > div > div > input, .stTextInput > div > div > input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--white) !important;
    border-radius: 4px !important;
}

/* Log box */
.log-box {
    background: #050505;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
    font-family: var(--mono);
    font-size: 0.75rem;
    line-height: 1.7;
    max-height: 260px;
    overflow-y: auto;
    color: #9e9e9e;
}
.log-box .log-info  { color: #81d4fa; }
.log-box .log-signal{ color: var(--orange); font-weight: 600; }
.log-box .log-buy   { color: var(--green); }
.log-box .log-sell  { color: var(--red); }
.log-box .log-warn  { color: #ffd54f; }

/* Signal card */
.sig-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 12px;
    position: relative;
}
.sig-card.buy  { border-left: 4px solid var(--green); }
.sig-card.sell { border-left: 4px solid var(--red); }
.sig-card.none { border-left: 4px solid var(--muted); }
.sig-header { font-size: 1.05rem; font-weight: 700; letter-spacing: 0.5px; }
.sig-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 1px;
    margin-left: 8px;
    vertical-align: middle;
}
.sig-badge.buy  { background: var(--green-dk); color: #fff; }
.sig-badge.sell { background: var(--red); color: #fff; }
.sig-badge.none { background: var(--muted); color: #fff; }
.sig-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin: 12px 0; }
.sig-item label { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; display: block; }
.sig-item span { font-family: var(--mono); font-size: 0.85rem; }
.conf-bar { height: 6px; border-radius: 3px; background: var(--border); margin-top: 4px; }
.conf-fill { height: 100%; border-radius: 3px; }
.reason-box { font-size: 0.78rem; color: #bbb; border-top: 1px solid var(--border); padding-top: 10px; margin-top: 10px; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Status pill */
.status-live {
    display: inline-flex; align-items: center; gap: 6px;
    background: #003018; border: 1px solid var(--green-dk);
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.75rem; font-weight: 600; color: var(--green);
}
.status-live::before { content: "●"; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.2} }

.status-off {
    display: inline-flex; align-items: center; gap: 6px;
    background: #1a0000; border: 1px solid #5c1a1a;
    border-radius: 20px; padding: 4px 12px;
    font-size: 0.75rem; color: var(--muted);
}
.status-off::before { content: "●"; color: var(--muted); }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = "ai_scanner.db"
LOG_CSV = "trade_log.csv"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            pair TEXT,
            timeframe TEXT,
            signal TEXT,
            entry REAL,
            stop_loss REAL,
            tp1 REAL, tp2 REAL, tp3 REAL,
            confidence REAL,
            trend TEXT,
            rr REAL,
            reason TEXT
        );

        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            open_time TEXT,
            close_time TEXT,
            pair TEXT,
            direction TEXT,
            entry REAL,
            exit_price REAL,
            stop_loss REAL,
            tp1 REAL, tp2 REAL, tp3 REAL,
            lot_size REAL,
            profit REAL,
            status TEXT,
            confidence REAL,
            reason TEXT
        );

        CREATE TABLE IF NOT EXISTS account_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            balance REAL,
            equity REAL,
            daily_pnl REAL
        );

        CREATE TABLE IF NOT EXISTS daily_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            total_trades INTEGER,
            wins INTEGER,
            losses INTEGER,
            gross_profit REAL,
            gross_loss REAL,
            net_pnl REAL,
            win_rate REAL
        );
    """)
    conn.commit()
    conn.close()

init_db()


# ─────────────────────────────────────────────────────────────────────────────
# MARKET CONFIG
# ─────────────────────────────────────────────────────────────────────────────
FOREX_PAIRS  = ["EUR/USD", "USD/CHF", "GBP/USD", "USD/JPY", "AUD/USD"]
CRYPTO_PAIRS = ["ETH/USD", "LTC/USD", "XRP/USD", "BCH/USD"]
SYNTH_PAIRS  = [
    "Boom 1000", "Boom 500", "Crash 1000", "Crash 500",
    "Volatility 10", "Volatility 25", "Volatility 50", "Volatility 75", "Volatility 100",
]
ALL_PAIRS = FOREX_PAIRS + CRYPTO_PAIRS + SYNTH_PAIRS
TIMEFRAMES = ["M1","M5","M15","M30","H1","H4","D1"]

# yfinance ticker map
YF_MAP = {
    "EUR/USD":"EURUSD=X", "USD/CHF":"CHF=X", "GBP/USD":"GBPUSD=X",
    "USD/JPY":"JPY=X",    "AUD/USD":"AUDUSD=X",
    "ETH/USD":"ETH-USD",  "LTC/USD":"LTC-USD",
    "XRP/USD":"XRP-USD",  "BCH/USD":"BCH-USD",
}
TF_MAP = {"M1":"1m","M5":"5m","M15":"15m","M30":"30m","H1":"1h","H4":"4h","D1":"1d"}
TF_PERIOD = {"M1":"1d","M5":"5d","M15":"5d","M30":"60d","H1":"60d","H4":"730d","D1":"730d"}

SYNTH_VOLATILITY = {
    "Boom 1000": (0.0002, 0.0015),
    "Boom 500":  (0.0003, 0.002),
    "Crash 1000":(0.0002, 0.0015),
    "Crash 500": (0.0003, 0.002),
    "Volatility 10":(0.00005, 0.0008),
    "Volatility 25":(0.0001, 0.0012),
    "Volatility 50":(0.0002, 0.0018),
    "Volatility 75":(0.0003, 0.0025),
    "Volatility 100":(0.0004, 0.003),
}


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
def init_session():
    defaults = {
        "bot_running": False,
        "account_balance": 10000.0,
        "equity": 10000.0,
        "daily_pnl": 0.0,
        "open_trades": [],
        "closed_trades": [],
        "signals": [],
        "logs": [],
        "scan_count": 0,
        "last_scan": None,
        "session_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "halt_trading": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def add_log(msg: str, level: str = "info"):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = {"ts": ts, "msg": msg, "level": level}
    st.session_state["logs"].insert(0, entry)
    st.session_state["logs"] = st.session_state["logs"][:200]

    with open(LOG_CSV, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow([ts, level.upper(), msg])


# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHING
# ─────────────────────────────────────────────────────────────────────────────
def fetch_ohlcv(pair: str, timeframe: str) -> pd.DataFrame:
    """Fetch OHLCV data – real from yfinance where available, synthetic otherwise."""
    if pair in SYNTH_PAIRS:
        return _synth_data(pair, 300)

    if not HAS_YFINANCE:
        return _synth_data(pair, 300)

    ticker = YF_MAP.get(pair)
    if not ticker:
        return _synth_data(pair, 300)
    try:
        tf  = TF_MAP.get(timeframe, "15m")
        per = TF_PERIOD.get(timeframe, "5d")
        df  = yf.download(ticker, period=per, interval=tf, progress=False, auto_adjust=True)
        if df.empty:
            return _synth_data(pair, 300)
        df = df[["Open","High","Low","Close","Volume"]].copy()
        df.columns = ["open","high","low","close","volume"]
        df.dropna(inplace=True)
        return df
    except Exception:
        return _synth_data(pair, 300)


def _synth_data(pair: str, bars: int = 300) -> pd.DataFrame:
    """Generate synthetic OHLCV data with realistic price behaviour."""
    vol_params = SYNTH_VOLATILITY.get(pair, (0.0001, 0.001))
    np.random.seed(hash(pair) % (2**31))

    # starting price
    base = {
        "EUR/USD": 1.0850, "USD/CHF": 0.9050, "GBP/USD": 1.2650,
        "USD/JPY": 149.50, "AUD/USD": 0.6550,
        "ETH/USD": 3200.0, "LTC/USD": 90.0,
        "XRP/USD": 0.55,   "BCH/USD": 350.0,
        "Boom 1000": 8500.0, "Boom 500": 4200.0,
        "Crash 1000": 8500.0, "Crash 500": 4200.0,
        "Volatility 10": 1000.0, "Volatility 25": 1000.0,
        "Volatility 50": 1000.0, "Volatility 75": 1000.0,
        "Volatility 100": 1000.0,
    }.get(pair, 1.0)

    # random walk with trend bias
    drift = np.random.choice([-1, 0, 0, 1]) * vol_params[0] * 0.5
    ret = np.random.normal(drift, vol_params[1], bars)
    prices = base * np.exp(np.cumsum(ret))

    opens   = prices.copy()
    closes  = np.roll(prices, -1); closes[-1] = prices[-1]
    hl_span = np.abs(np.random.normal(0, vol_params[1] * 0.5, bars)) * prices
    highs   = np.maximum(opens, closes) + hl_span
    lows    = np.minimum(opens, closes) - hl_span
    volumes = np.random.randint(500, 50000, bars).astype(float)

    idx = pd.date_range(end=datetime.now(), periods=bars, freq="15min")
    return pd.DataFrame({"open": opens, "high": highs, "low": lows,
                         "close": closes, "volume": volumes}, index=idx)


# ─────────────────────────────────────────────────────────────────────────────
# TECHNICAL INDICATORS
# ─────────────────────────────────────────────────────────────────────────────
def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()


# ─────────────────────────────────────────────────────────────────────────────
# SMC / ICT ANALYSIS ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def detect_swing_points(df: pd.DataFrame, lookback: int = 5):
    highs, lows = [], []
    for i in range(lookback, len(df) - lookback):
        if df["high"].iloc[i] == df["high"].iloc[i-lookback:i+lookback+1].max():
            highs.append(i)
        if df["low"].iloc[i] == df["low"].iloc[i-lookback:i+lookback+1].min():
            lows.append(i)
    return highs, lows


def detect_market_structure(df: pd.DataFrame):
    swing_highs, swing_lows = detect_swing_points(df)
    if len(swing_highs) < 2 or len(swing_lows) < 2:
        return "RANGING", False, False

    last_hh = df["high"].iloc[swing_highs[-1]]
    prev_hh = df["high"].iloc[swing_highs[-2]]
    last_ll = df["low"].iloc[swing_lows[-1]]
    prev_ll = df["low"].iloc[swing_lows[-2]]

    bos  = False
    choch= False
    if last_hh > prev_hh and last_ll > prev_ll:
        structure = "BULLISH"
        if last_hh > prev_hh: bos = True
    elif last_hh < prev_hh and last_ll < prev_ll:
        structure = "BEARISH"
        if last_ll < prev_ll: bos = True
    else:
        structure = "RANGING"
        choch = True
    return structure, bos, choch


def detect_order_blocks(df: pd.DataFrame, direction: str):
    """Find last significant order block before a move."""
    ob_high, ob_low = None, None
    for i in range(len(df) - 20, len(df) - 2):
        body = abs(df["close"].iloc[i] - df["open"].iloc[i])
        avg_body = abs(df["close"] - df["open"]).rolling(10).mean().iloc[i]
        if body > avg_body * 1.5:
            if direction == "BULLISH" and df["close"].iloc[i] < df["open"].iloc[i]:
                ob_high = df["high"].iloc[i]
                ob_low  = df["low"].iloc[i]
            elif direction == "BEARISH" and df["close"].iloc[i] > df["open"].iloc[i]:
                ob_high = df["high"].iloc[i]
                ob_low  = df["low"].iloc[i]
    return ob_high, ob_low


def detect_fvg(df: pd.DataFrame):
    """Detect Fair Value Gap."""
    fvg_up, fvg_dn = [], []
    for i in range(2, len(df)):
        c1h = df["high"].iloc[i-2]
        c3l = df["low"].iloc[i]
        if c3l > c1h:
            fvg_up.append((c1h, c3l))
        c1l = df["low"].iloc[i-2]
        c3h = df["high"].iloc[i]
        if c3h < c1l:
            fvg_dn.append((c1l, c3h))
    return fvg_up[-1] if fvg_up else None, fvg_dn[-1] if fvg_dn else None


def detect_liquidity_sweep(df: pd.DataFrame):
    """Detect recent liquidity sweep above swing high or below swing low."""
    swing_highs, swing_lows = detect_swing_points(df, lookback=3)
    if not swing_highs or not swing_lows:
        return False, False

    recent_sh = df["high"].iloc[swing_highs[-1]]
    recent_sl = df["low"].iloc[swing_lows[-1]]
    last_high = df["high"].iloc[-1]
    last_low  = df["low"].iloc[-1]
    last_close= df["close"].iloc[-1]

    swept_high = last_high > recent_sh and last_close < recent_sh
    swept_low  = last_low  < recent_sl and last_close > recent_sl
    return swept_high, swept_low


def detect_price_action(df: pd.DataFrame):
    """Detect pin bars, engulfing candles."""
    c  = df.iloc[-1]
    pc = df.iloc[-2]

    body    = abs(c["close"] - c["open"])
    rng     = c["high"] - c["low"] + 1e-9
    up_wick = c["high"] - max(c["close"], c["open"])
    dn_wick = min(c["close"], c["open"]) - c["low"]

    pin_bear = (up_wick / rng > 0.6) and (body / rng < 0.2)
    pin_bull = (dn_wick / rng > 0.6) and (body / rng < 0.2)

    pbody = abs(pc["close"] - pc["open"])
    engulf_bull = (c["close"] > pc["open"] and c["open"] < pc["close"] and
                   c["close"] > c["open"] and pbody > 0)
    engulf_bear = (c["close"] < pc["open"] and c["open"] > pc["close"] and
                   c["close"] < c["open"] and pbody > 0)

    return pin_bull, pin_bear, engulf_bull, engulf_bear


def calculate_support_resistance(df: pd.DataFrame):
    swing_highs, swing_lows = detect_swing_points(df)
    supports    = sorted([df["low"].iloc[i]  for i in swing_lows[-4:]],  reverse=True)[:3]
    resistances = sorted([df["high"].iloc[i] for i in swing_highs[-4:]], reverse=True)[:3]
    return supports, resistances


# ─────────────────────────────────────────────────────────────────────────────
# AI SCORING ENGINE
# ─────────────────────────────────────────────────────────────────────────────
WEIGHTS = {
    "market_structure":  25,
    "smc_confirmation":  25,
    "rsi_confirmation":  15,
    "ema_trend":         15,
    "liquidity_sweep":   10,
    "price_action":      10,
}


def score_signal(df: pd.DataFrame, direction: str) -> dict:
    scores = {}

    # ── Market Structure ──────────────────────────────────
    structure, bos, choch = detect_market_structure(df)
    if direction == "BUY":
        ms = 100 if structure == "BULLISH" else (50 if structure == "RANGING" else 0)
    else:
        ms = 100 if structure == "BEARISH" else (50 if structure == "RANGING" else 0)
    if bos:  ms = min(ms + 20, 100)
    scores["market_structure"] = ms

    # ── SMC Confirmation ──────────────────────────────────
    ob_h, ob_l = detect_order_blocks(df, structure)
    fvg_up, fvg_dn = detect_fvg(df)
    price = df["close"].iloc[-1]
    smc = 0
    if ob_h and ob_l:
        if direction == "BUY"  and ob_l <= price <= ob_h: smc += 50
        if direction == "SELL" and ob_l <= price <= ob_h: smc += 50
    if direction == "BUY"  and fvg_up: smc += 50
    if direction == "SELL" and fvg_dn:  smc += 50
    scores["smc_confirmation"] = min(smc, 100)

    # ── RSI ───────────────────────────────────────────────
    r = rsi(df["close"]).iloc[-1]
    if direction == "BUY":
        rsi_score = 100 if r < 40 else (70 if r < 55 else 30)
    else:
        rsi_score = 100 if r > 60 else (70 if r > 45 else 30)
    scores["rsi_confirmation"] = rsi_score

    # ── EMA Trend ─────────────────────────────────────────
    e50  = ema(df["close"], 50).iloc[-1]
    e200 = ema(df["close"], 200).iloc[-1]
    if direction == "BUY":
        ema_score = 100 if price > e50 > e200 else (60 if price > e200 else 0)
    else:
        ema_score = 100 if price < e50 < e200 else (60 if price < e200 else 0)
    scores["ema_trend"] = ema_score

    # ── Liquidity Sweep ───────────────────────────────────
    swept_high, swept_low = detect_liquidity_sweep(df)
    if direction == "BUY"  and swept_low:  scores["liquidity_sweep"] = 100
    elif direction == "SELL" and swept_high: scores["liquidity_sweep"] = 100
    else: scores["liquidity_sweep"] = 0

    # ── Price Action ──────────────────────────────────────
    pb, ps, eb, es = detect_price_action(df)
    if direction == "BUY":
        pa = 100 if (pb or eb) else 0
    else:
        pa = 100 if (ps or es) else 0
    scores["price_action"] = pa

    # ── Weighted confidence ───────────────────────────────
    confidence = sum(scores[k] * WEIGHTS[k] / 100 for k in WEIGHTS)
    return scores, confidence, structure, r


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def generate_signal(pair: str, timeframe: str,
                    account_balance: float, risk_pct: float,
                    lot_size: float) -> dict:
    df = fetch_ohlcv(pair, timeframe)
    if df is None or len(df) < 210:
        return _no_trade(pair, timeframe, "Insufficient data")

    price   = float(df["close"].iloc[-1])
    atr_val = float(atr(df).iloc[-1])

    # ── Determine candidate direction ─────────────────────
    structure, bos, choch = detect_market_structure(df)
    r_val = float(rsi(df["close"]).iloc[-1])
    e50v  = float(ema(df["close"], 50).iloc[-1])

    if structure == "BULLISH" and price > e50v:
        direction = "BUY"
    elif structure == "BEARISH" and price < e50v:
        direction = "SELL"
    else:
        direction = "BUY" if r_val < 45 else "SELL"

    scores, confidence, trend, rsi_v = score_signal(df, direction)

    if confidence < 75:
        return _no_trade(pair, timeframe, f"Confidence {confidence:.1f}% < 75% threshold")

    # ── Entry & Exits ─────────────────────────────────────
    supports, resistances = calculate_support_resistance(df)
    sl_dist  = atr_val * 1.5
    tp_mult  = [1.5, 2.5, 4.0]

    if direction == "BUY":
        entry  = price
        sl     = round(entry - sl_dist, 5)
        tp1    = round(entry + atr_val * tp_mult[0], 5)
        tp2    = round(entry + atr_val * tp_mult[1], 5)
        tp3    = round(entry + atr_val * tp_mult[2], 5)
    else:
        entry  = price
        sl     = round(entry + sl_dist, 5)
        tp1    = round(entry - atr_val * tp_mult[0], 5)
        tp2    = round(entry - atr_val * tp_mult[1], 5)
        tp3    = round(entry - atr_val * tp_mult[2], 5)

    rr = round(atr_val * tp_mult[1] / sl_dist, 2)

    # ── Position size ─────────────────────────────────────
    risk_amount   = account_balance * (risk_pct / 100)
    auto_lot_size = round(risk_amount / (sl_dist * 100000 + 1e-9), 2)
    auto_lot_size = max(0.01, min(auto_lot_size, lot_size))

    # ── Build reason ─────────────────────────────────────
    _, swept_high, swept_low = (*detect_liquidity_sweep(df),)  # unpack 2
    pa = detect_price_action(df)
    reason_parts = [
        f"Market structure is {trend}.",
        f"BOS confirmed." if bos else "",
        f"CHOCH detected — trend shift possible." if choch else "",
        f"Liquidity sweep {'above swing high' if swept_high else 'below swing low'} detected." if (swept_high or swept_low) else "",
        f"RSI at {rsi_v:.1f} — {'oversold, reversal likely' if rsi_v < 35 else 'overbought, sell pressure' if rsi_v > 65 else 'neutral zone'}.",
        f"Price {'above' if price > e50v else 'below'} EMA 50 — trend {'confirmed' if direction=='BUY' and price > e50v else 'confirmed' if direction=='SELL' and price < e50v else 'divergence warning'}.",
        f"Order block identified at entry zone.",
        f"{'Bullish' if direction=='BUY' else 'Bearish'} price action pattern present.",
    ]
    reason = " ".join(p for p in reason_parts if p)

    sig = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pair": pair,
        "timeframe": timeframe,
        "signal": direction,
        "entry": round(entry, 5),
        "stop_loss": sl,
        "tp1": tp1, "tp2": tp2, "tp3": tp3,
        "risk_reward": rr,
        "confidence": round(confidence, 1),
        "trend": trend,
        "supports": supports,
        "resistances": resistances,
        "lot_size": auto_lot_size,
        "reason": reason,
        "scores": scores,
    }

    _save_signal(sig)
    return sig


def _no_trade(pair, timeframe, reason):
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pair": pair, "timeframe": timeframe,
        "signal": "NO TRADE", "confidence": 0,
        "reason": reason, "trend": "—",
        "entry": 0, "stop_loss": 0,
        "tp1": 0, "tp2": 0, "tp3": 0,
        "risk_reward": 0,
        "supports": [], "resistances": [],
        "lot_size": 0, "scores": {},
    }

def _unpack_sweep(result):
    """Handle both 2-value and 3-value returns from detect_liquidity_sweep."""
    if len(result) == 2:
        return result[0], result[1]
    return result[0], result[1]


def _save_signal(sig):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO signals (timestamp,pair,timeframe,signal,entry,stop_loss,
                                 tp1,tp2,tp3,confidence,trend,rr,reason)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sig["timestamp"], sig["pair"], sig["timeframe"], sig["signal"],
              sig["entry"], sig["stop_loss"], sig["tp1"], sig["tp2"], sig["tp3"],
              sig["confidence"], sig["trend"], sig["risk_reward"], sig["reason"]))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# TRADE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def open_trade(sig: dict):
    trade = {**sig, "id": int(time.time()*1000), "status": "OPEN",
             "open_time": sig["timestamp"], "close_time": None,
             "exit_price": None, "profit": 0.0}
    st.session_state["open_trades"].append(trade)
    add_log(f"📈 Trade OPEN — {sig['pair']} {sig['signal']} @ {sig['entry']}  "
            f"SL:{sig['stop_loss']}  TP1:{sig['tp1']}", "buy" if sig["signal"]=="BUY" else "sell")
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO trades (open_time,pair,direction,entry,stop_loss,
                                tp1,tp2,tp3,lot_size,status,confidence,reason)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (sig["timestamp"],sig["pair"],sig["signal"],sig["entry"],sig["stop_loss"],
              sig["tp1"],sig["tp2"],sig["tp3"],sig["lot_size"],"OPEN",
              sig["confidence"],sig["reason"]))
        conn.commit(); conn.close()
    except Exception:
        pass


def close_trade(trade: dict, exit_price: float, reason: str = "Manual"):
    direction  = trade["signal"]
    pip_value  = 10 * trade.get("lot_size", 0.01)
    price_diff = (exit_price - trade["entry"]) if direction=="BUY" else (trade["entry"] - exit_price)
    profit     = round(price_diff * pip_value * 10000, 2)

    trade.update({"status":"CLOSED","close_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                  "exit_price":exit_price,"profit":profit})

    st.session_state["open_trades"]   = [t for t in st.session_state["open_trades"] if t["id"]!=trade["id"]]
    st.session_state["closed_trades"].append(trade)
    st.session_state["daily_pnl"]    += profit
    st.session_state["account_balance"] += profit
    st.session_state["equity"]         = st.session_state["account_balance"]

    add_log(f"{'✅' if profit>=0 else '❌'} Trade CLOSED — {trade['pair']} {direction} "
            f"@ {exit_price}  P&L: {'+'if profit>=0 else ''}{profit:.2f}  ({reason})",
            "buy" if profit>=0 else "sell")


def simulate_trade_outcomes(cfg: dict):
    """Simulate SL/TP hits on open trades using latest price."""
    for trade in list(st.session_state["open_trades"]):
        df = fetch_ohlcv(trade["pair"], trade["timeframe"])
        if df is None or df.empty: continue
        cur = float(df["close"].iloc[-1])

        if trade["signal"] == "BUY":
            if cur <= trade["stop_loss"]:
                close_trade(trade, trade["stop_loss"], "Stop Loss")
            elif cur >= trade["tp3"]:
                close_trade(trade, trade["tp3"], "TP3 ✨")
            elif cur >= trade["tp2"]:
                close_trade(trade, trade["tp2"], "TP2")
            elif cur >= trade["tp1"]:
                close_trade(trade, trade["tp1"], "TP1")
        else:
            if cur >= trade["stop_loss"]:
                close_trade(trade, trade["stop_loss"], "Stop Loss")
            elif cur <= trade["tp3"]:
                close_trade(trade, trade["tp3"], "TP3 ✨")
            elif cur <= trade["tp2"]:
                close_trade(trade, trade["tp2"], "TP2")
            elif cur <= trade["tp1"]:
                close_trade(trade, trade["tp1"], "TP1")


# ─────────────────────────────────────────────────────────────────────────────
# CHART
# ─────────────────────────────────────────────────────────────────────────────
def render_chart(pair: str, timeframe: str):
    df = fetch_ohlcv(pair, timeframe)
    if df is None or df.empty:
        st.info("No chart data available.")
        return

    if not HAS_PLOTLY:
        st.line_chart(df["close"].tail(100))
        return

    df_plot = df.tail(120).copy()
    df_plot["ema50"]  = ema(df["close"], 50).tail(120).values
    df_plot["ema200"] = ema(df["close"], 200).tail(120).values

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df_plot.index,
        open=df_plot["open"], high=df_plot["high"],
        low=df_plot["low"],  close=df_plot["close"],
        name=pair,
        increasing_line_color="#00c853",
        decreasing_line_color="#cc5500",
        increasing_fillcolor="#00c853",
        decreasing_fillcolor="#cc5500",
    ))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["ema50"],
                             line=dict(color="#cc5500", width=1.5), name="EMA 50"))
    fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["ema200"],
                             line=dict(color="#ffffff", width=1.5, dash="dot"), name="EMA 200"))

    # Add open trades to chart
    for t in st.session_state["open_trades"]:
        if t["pair"] == pair:
            col = "#00c853" if t["signal"]=="BUY" else "#e53935"
            for level, label in [(t["entry"],"Entry"),(t["stop_loss"],"SL"),
                                  (t["tp1"],"TP1"),(t["tp2"],"TP2"),(t["tp3"],"TP3")]:
                fig.add_hline(y=level, line_dash="dash",
                              line_color=col if "TP" in label else ("#e53935" if label=="SL" else "#ffffff"),
                              opacity=0.7, annotation_text=label,
                              annotation_font_size=10, annotation_font_color="#ffffff")

    fig.update_layout(
        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
        font=dict(color="#f0f0f0", family="Space Grotesk"),
        xaxis=dict(gridcolor="#1a1a1a", showgrid=True),
        yaxis=dict(gridcolor="#1a1a1a", showgrid=True),
        legend=dict(bgcolor="#111111", bordercolor="#222222"),
        margin=dict(l=0,r=0,t=30,b=0), height=420,
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIGNAL CARD RENDERER
# ─────────────────────────────────────────────────────────────────────────────
def render_signal_card(sig: dict):
    direction = sig.get("signal","NO TRADE")
    css_class = "buy" if direction=="BUY" else "sell" if direction=="SELL" else "none"
    icon = "🟢" if direction=="BUY" else "🔴" if direction=="SELL" else "⚪"
    conf = sig.get("confidence", 0)
    conf_color = "#00c853" if conf>=80 else "#cc5500" if conf>=65 else "#666"

    if direction in ("BUY","SELL"):
        body = f"""
        <div class="sig-grid">
            <div class="sig-item"><label>Entry</label><span>{sig['entry']}</span></div>
            <div class="sig-item"><label>Stop Loss</label><span style="color:#e53935">{sig['stop_loss']}</span></div>
            <div class="sig-item"><label>R:R</label><span>{sig.get('risk_reward','—')}</span></div>
            <div class="sig-item"><label>TP 1</label><span style="color:#00c853">{sig['tp1']}</span></div>
            <div class="sig-item"><label>TP 2</label><span style="color:#00c853">{sig['tp2']}</span></div>
            <div class="sig-item"><label>TP 3</label><span style="color:#00c853">{sig['tp3']}</span></div>
        </div>
        <div style="margin:8px 0">
            <span style="font-size:0.7rem;color:#666;text-transform:uppercase;letter-spacing:1px">Confidence</span>
            <span style="font-family:monospace;font-weight:700;color:{conf_color};margin-left:8px">{conf}%</span>
            <div class="conf-bar"><div class="conf-fill" style="width:{conf}%;background:{conf_color}"></div></div>
        </div>
        """
    else:
        body = f'<div style="color:#666;font-size:0.85rem;padding:8px 0">{sig.get("reason","—")}</div>'

    st.markdown(f"""
    <div class="sig-card {css_class}">
        <div class="sig-header">
            {icon} {sig['pair']}
            <span class="sig-badge {css_class}">{direction}</span>
            <span style="font-size:0.7rem;color:#666;font-weight:400;margin-left:8px">
                {sig['timeframe']} · {sig.get('trend','—')} · {sig['timestamp'][-8:]}
            </span>
        </div>
        {body}
        <div class="reason-box">{sig.get('reason','')[:280]}</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCAN LOOP (runs once per Streamlit rerun while bot_running=True)
# ─────────────────────────────────────────────────────────────────────────────
def run_scan_cycle(selected_pairs, timeframe, account_balance, risk_pct,
                   lot_size, max_trades, daily_loss):
    if st.session_state.get("halt_trading"):
        add_log("⛔ Trading halted — daily loss limit reached.", "warn")
        return

    if abs(st.session_state["daily_pnl"]) >= daily_loss and st.session_state["daily_pnl"] < 0:
        st.session_state["halt_trading"] = True
        add_log(f"⛔ Daily loss limit ${daily_loss:.2f} hit. All trading halted.", "warn")
        return

    st.session_state["scan_count"] += 1
    st.session_state["last_scan"]   = datetime.now().strftime("%H:%M:%S")
    add_log(f"🔍 Scan #{st.session_state['scan_count']} started — {len(selected_pairs)} pairs", "info")

    new_signals = []
    for pair in selected_pairs:
        try:
            sig = generate_signal(pair, timeframe, account_balance, risk_pct, lot_size)
            new_signals.append(sig)

            if sig["signal"] in ("BUY","SELL"):
                open_count = len([t for t in st.session_state["open_trades"] if t["pair"]==pair])
                total_open = len(st.session_state["open_trades"])
                if open_count == 0 and total_open < max_trades:
                    open_trade(sig)
                    add_log(f"📡 Signal: {pair} {sig['signal']} — Conf:{sig['confidence']}%", "signal")
                else:
                    add_log(f"ℹ️ {pair} signal skipped — max trades reached or duplicate", "warn")
            else:
                add_log(f"〰 {pair}: {sig['reason'][:60]}", "info")
        except Exception as e:
            add_log(f"⚠️ Error scanning {pair}: {str(e)[:60]}", "warn")

    # simulate outcomes on existing open trades
    simulate_trade_outcomes({"pairs": selected_pairs})

    # prepend new signals (most recent first), keep 50
    st.session_state["signals"] = new_signals + st.session_state["signals"]
    st.session_state["signals"] = st.session_state["signals"][:50]


# ─────────────────────────────────────────────────────────────────────────────
# STATS HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def compute_stats():
    closed = st.session_state["closed_trades"]
    if not closed:
        return {"wins":0, "losses":0, "win_rate":0.0,
                "gross_profit":0.0, "gross_loss":0.0, "avg_rr":0.0}
    wins      = [t for t in closed if t.get("profit",0) >= 0]
    losses    = [t for t in closed if t.get("profit",0) <  0]
    win_rate  = round(len(wins)/len(closed)*100, 1) if closed else 0
    g_profit  = sum(t.get("profit",0) for t in wins)
    g_loss    = sum(t.get("profit",0) for t in losses)
    avg_rr    = round(sum(t.get("risk_reward",0) for t in closed)/len(closed), 2) if closed else 0
    return {"wins":len(wins),"losses":len(losses),"win_rate":win_rate,
            "gross_profit":round(g_profit,2),"gross_loss":round(g_loss,2),"avg_rr":avg_rr}


# ─────────────────────────────────────────────────────────────────────────────
# UI — SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    account_type = st.selectbox("Account Type", ["Forex","Crypto","Synthetics","All Markets"])
    if account_type == "Forex":
        pair_pool = FOREX_PAIRS
    elif account_type == "Crypto":
        pair_pool = CRYPTO_PAIRS
    elif account_type == "Synthetics":
        pair_pool = SYNTH_PAIRS
    else:
        pair_pool = ALL_PAIRS

    selected_pairs = st.multiselect("Select Pairs", pair_pool, default=pair_pool[:3])
    timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=2)

    st.markdown("---")
    st.markdown("**Risk Management**")
    account_balance_input = st.number_input("Account Balance ($)", min_value=100.0,
                                             value=st.session_state["account_balance"], step=100.0)
    if account_balance_input != st.session_state["account_balance"]:
        st.session_state["account_balance"] = account_balance_input
        st.session_state["equity"] = account_balance_input

    risk_pct     = st.slider("Risk Per Trade (%)", 0.5, 5.0, 1.0, 0.1)
    lot_size     = st.number_input("Max Lot Size", 0.01, 100.0, 0.10, 0.01)
    daily_loss   = st.number_input("Daily Loss Limit ($)", 0.0, 10000.0, 500.0, 50.0)
    daily_target = st.number_input("Daily Profit Target ($)", 0.0, 10000.0, 1000.0, 50.0)
    max_trades   = st.number_input("Max Open Trades", 1, 20, 5, 1)

    st.markdown("---")
    st.markdown("**Scan Interval**")
    scan_interval = st.select_slider("Seconds between scans",
                                     options=[30,60,120,180,300], value=60)

    st.markdown("---")
    # BOT CONTROLS
    col_s, col_x = st.columns(2)
    with col_s:
        st.markdown('<div class="btn-start">', unsafe_allow_html=True)
        if st.button("▶ START", use_container_width=True):
            st.session_state["bot_running"] = True
            st.session_state["halt_trading"] = False
            add_log("🟢 Bot STARTED", "signal")
        st.markdown("</div>", unsafe_allow_html=True)
    with col_x:
        st.markdown('<div class="btn-stop">', unsafe_allow_html=True)
        if st.button("⏹ STOP", use_container_width=True):
            st.session_state["bot_running"] = False
            add_log("🔴 Bot STOPPED", "warn")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("❌ Close All Trades", use_container_width=True):
        for t in list(st.session_state["open_trades"]):
            df = fetch_ohlcv(t["pair"], t["timeframe"])
            ex = float(df["close"].iloc[-1]) if df is not None and not df.empty else t["entry"]
            close_trade(t, ex, "Manual Close All")
        add_log("⚠️ All trades closed manually", "warn")

    if st.button("🔄 Reset Session", use_container_width=True):
        for k in ["open_trades","closed_trades","signals","logs","daily_pnl","scan_count"]:
            st.session_state[k] = [] if isinstance(st.session_state[k], list) else 0
        st.session_state["daily_pnl"] = 0.0
        st.session_state["halt_trading"] = False
        add_log("♻️ Session reset", "info")

    st.markdown("---")
    # status indicator
    if st.session_state["bot_running"]:
        st.markdown('<span class="status-live">LIVE SCANNING</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="status-off">BOT OFFLINE</span>', unsafe_allow_html=True)

    if st.session_state.get("last_scan"):
        st.caption(f"Last scan: {st.session_state['last_scan']}")


# ─────────────────────────────────────────────────────────────────────────────
# UI — HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:16px;margin-bottom:4px">
    <span style="font-size:2.2rem;font-weight:800;color:#cc5500;letter-spacing:-1px">📡 AI SCANNER</span>
    <span style="font-size:0.75rem;color:#666;font-family:monospace;margin-top:8px">
        SMC · ICT · PRICE ACTION · MULTI-TIMEFRAME
    </span>
</div>
<div style="font-size:0.78rem;color:#555;margin-bottom:20px;font-family:monospace">
    Emevine AI Trading System &nbsp;·&nbsp; Session: """ + st.session_state["session_start"] + """
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# UI — METRICS ROW
# ─────────────────────────────────────────────────────────────────────────────
stats = compute_stats()
pnl   = st.session_state["daily_pnl"]

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1: st.metric("Balance", f"${st.session_state['account_balance']:,.2f}")
with m2: st.metric("Equity",  f"${st.session_state['equity']:,.2f}")
with m3: st.metric("Daily P&L", f"${pnl:+,.2f}", delta=f"{pnl/st.session_state['account_balance']*100:+.2f}%")
with m4: st.metric("Win Rate", f"{stats['win_rate']}%",
                    delta=f"{stats['wins']}W / {stats['losses']}L")
with m5: st.metric("Open Trades",   len(st.session_state["open_trades"]))
with m6: st.metric("Closed Trades", len(st.session_state["closed_trades"]))

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# UI — MAIN TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_chart, tab_signals, tab_open, tab_closed, tab_log, tab_db = st.tabs([
    "📊 Live Chart", "📡 Signals", "📂 Open Trades", "📁 Closed Trades", "📋 Trade Log", "🗄️ Database"
])

# ── TAB 1 — Chart ──────────────────────────────────────────────────────────
with tab_chart:
    chart_pair = st.selectbox("Chart Pair", selected_pairs if selected_pairs else ["EUR/USD"],
                               key="chart_pair")
    chart_tf   = st.selectbox("Chart Timeframe", TIMEFRAMES, index=2, key="chart_tf")
    render_chart(chart_pair, chart_tf)

    # RSI mini-chart
    df_rsi = fetch_ohlcv(chart_pair, chart_tf)
    if df_rsi is not None and not df_rsi.empty:
        rsi_vals = rsi(df_rsi["close"]).tail(60)
        if HAS_PLOTLY:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(y=rsi_vals.values, line=dict(color="#cc5500",width=1.5), name="RSI 14"))
            fig_rsi.add_hline(y=70, line_dash="dot", line_color="#e53935", opacity=0.5)
            fig_rsi.add_hline(y=30, line_dash="dot", line_color="#00c853", opacity=0.5)
            fig_rsi.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                                   height=120, margin=dict(l=0,r=0,t=0,b=0),
                                   showlegend=False, font=dict(color="#f0f0f0"),
                                   yaxis=dict(gridcolor="#1a1a1a"),
                                   xaxis=dict(gridcolor="#1a1a1a"))
            st.plotly_chart(fig_rsi, use_container_width=True)

# ── TAB 2 — Signals ────────────────────────────────────────────────────────
with tab_signals:
    col_sig, col_detail = st.columns([3, 2])
    with col_sig:
        if st.session_state["bot_running"] and selected_pairs:
            st.markdown('<div style="color:#00c853;font-size:0.8rem;margin-bottom:8px">● Auto-scanning active</div>',
                        unsafe_allow_html=True)
        else:
            if st.button("🔍 Run Manual Scan"):
                if selected_pairs:
                    run_scan_cycle(selected_pairs, timeframe,
                                   st.session_state["account_balance"],
                                   risk_pct, lot_size, int(max_trades), daily_loss)

        if not st.session_state["signals"]:
            st.info("No signals yet. Start the bot or run a manual scan.")
        else:
            for sig in st.session_state["signals"][:15]:
                render_signal_card(sig)

    with col_detail:
        st.markdown("#### 📊 Score Breakdown")
        if st.session_state["signals"]:
            latest_trade_sigs = [s for s in st.session_state["signals"] if s["signal"] in ("BUY","SELL")]
            if latest_trade_sigs and HAS_PLOTLY:
                sig0 = latest_trade_sigs[0]
                sc   = sig0.get("scores", {})
                if sc:
                    labels = list(WEIGHTS.keys())
                    values = [sc.get(k, 0) for k in labels]
                    fig_r  = go.Figure(go.Bar(
                        x=[l.replace("_"," ").title() for l in labels],
                        y=values, marker_color="#cc5500",
                        text=[f"{v}%" for v in values], textposition="auto",
                        textfont=dict(size=10)
                    ))
                    fig_r.update_layout(
                        paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                        font=dict(color="#f0f0f0", size=10), height=260,
                        margin=dict(l=0,r=0,t=10,b=0),
                        yaxis=dict(range=[0,100], gridcolor="#1a1a1a"),
                        xaxis=dict(gridcolor="#1a1a1a"),
                    )
                    st.plotly_chart(fig_r, use_container_width=True)
                    st.markdown(f"**{sig0['pair']}** · {sig0['signal']} · "
                                f"Conf: **{sig0['confidence']}%**")

        st.markdown("#### Market Overview")
        for pair in (selected_pairs or ALL_PAIRS[:5]):
            df_q = fetch_ohlcv(pair, "H1")
            if df_q is not None and not df_q.empty:
                p = float(df_q["close"].iloc[-1])
                chg = (p - float(df_q["close"].iloc[-2])) / float(df_q["close"].iloc[-2]) * 100
                color = "#00c853" if chg >= 0 else "#e53935"
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:6px 0;border-bottom:1px solid #1a1a1a;font-size:0.82rem">'
                    f'<span>{pair}</span>'
                    f'<span style="font-family:monospace">{p:.5f}</span>'
                    f'<span style="color:{color};font-family:monospace">'
                    f'{"+" if chg>=0 else ""}{chg:.3f}%</span></div>',
                    unsafe_allow_html=True)

# ── TAB 3 — Open Trades ────────────────────────────────────────────────────
with tab_open:
    open_t = st.session_state["open_trades"]
    if not open_t:
        st.info("No open trades.")
    else:
        rows = []
        for t in open_t:
            df_t = fetch_ohlcv(t["pair"], t.get("timeframe","M15"))
            cur  = float(df_t["close"].iloc[-1]) if df_t is not None and not df_t.empty else t["entry"]
            dir_ = t["signal"]
            unrl = (cur - t["entry"]) if dir_=="BUY" else (t["entry"] - cur)
            rows.append({
                "Pair": t["pair"], "Dir": t["signal"],
                "Entry": t["entry"], "SL": t["stop_loss"],
                "TP1": t["tp1"], "TP2": t["tp2"], "TP3": t["tp3"],
                "Lot": t.get("lot_size",0.01), "Curr": round(cur,5),
                "Unrlzd": round(unrl*10000*t.get("lot_size",0.01)*10, 2),
                "Conf%": t.get("confidence",0),
                "Opened": t.get("open_time","—")[-8:],
            })
        df_open = pd.DataFrame(rows)
        st.dataframe(df_open, use_container_width=True, hide_index=True)

        if st.button("Close All Open Trades"):
            for t in list(st.session_state["open_trades"]):
                df_c = fetch_ohlcv(t["pair"], t.get("timeframe","M15"))
                ex   = float(df_c["close"].iloc[-1]) if df_c is not None and not df_c.empty else t["entry"]
                close_trade(t, ex, "Manual")

# ── TAB 4 — Closed Trades ──────────────────────────────────────────────────
with tab_closed:
    closed_t = st.session_state["closed_trades"]
    if not closed_t:
        st.info("No closed trades yet.")
    else:
        rows = []
        for t in closed_t:
            rows.append({
                "Pair": t["pair"], "Dir": t["signal"],
                "Entry": t.get("entry",0), "Exit": t.get("exit_price",0),
                "SL": t["stop_loss"], "TP1": t["tp1"],
                "P&L ($)": t.get("profit",0),
                "Lot": t.get("lot_size",0.01),
                "R:R": t.get("risk_reward",0),
                "Conf%": t.get("confidence",0),
                "Status": t.get("status","CLOSED"),
                "Opened": t.get("open_time","—")[-8:],
                "Closed": t.get("close_time","—")[-8:] if t.get("close_time") else "—",
            })
        df_closed = pd.DataFrame(rows)

        # colour P&L
        def color_pnl(val):
            return f"color: {'#00c853' if val >= 0 else '#e53935'}"

        st.dataframe(df_closed, use_container_width=True, hide_index=True)

        st.markdown("---")
        g1, g2, g3, g4 = st.columns(4)
        with g1: st.metric("Total Closed", len(closed_t))
        with g2: st.metric("Gross Profit", f"${stats['gross_profit']:,.2f}")
        with g3: st.metric("Gross Loss",   f"${abs(stats['gross_loss']):,.2f}")
        with g4: st.metric("Net P&L",      f"${stats['gross_profit']+stats['gross_loss']:,.2f}")

        if HAS_PLOTLY and len(closed_t) > 1:
            cumulative = pd.Series([t.get("profit",0) for t in closed_t]).cumsum()
            fig_eq = go.Figure(go.Scatter(
                y=cumulative, fill="tozeroy",
                line=dict(color="#00c853" if cumulative.iloc[-1]>=0 else "#cc5500", width=2),
                fillcolor="rgba(0,200,83,0.08)" if cumulative.iloc[-1]>=0 else "rgba(204,85,0,0.08)"
            ))
            fig_eq.update_layout(paper_bgcolor="#0a0a0a", plot_bgcolor="#0a0a0a",
                                  height=200, margin=dict(l=0,r=0,t=20,b=0),
                                  font=dict(color="#f0f0f0"),
                                  title=dict(text="Equity Curve", font=dict(size=13)),
                                  yaxis=dict(gridcolor="#1a1a1a"),
                                  xaxis=dict(gridcolor="#1a1a1a"))
            st.plotly_chart(fig_eq, use_container_width=True)

# ── TAB 5 — Trade Log ──────────────────────────────────────────────────────
with tab_log:
    logs = st.session_state["logs"]
    if not logs:
        st.info("No log entries yet.")
    else:
        level_map = {
            "info":"log-info","signal":"log-signal",
            "buy":"log-buy","sell":"log-sell","warn":"log-warn"
        }
        lines = "".join(
            f'<div class="{level_map.get(l["level"],"")}">[{l["ts"]}] {l["msg"]}</div>'
            for l in logs[:100]
        )
        st.markdown(f'<div class="log-box">{lines}</div>', unsafe_allow_html=True)

        if st.button("Export Log CSV"):
            df_log = pd.DataFrame(logs)
            st.download_button("⬇ Download trade_log.csv",
                                df_log.to_csv(index=False), "trade_log.csv", "text/csv")

# ── TAB 6 — Database ───────────────────────────────────────────────────────
with tab_db:
    st.markdown("#### 🗄️ SQLite — Live Records")
    db_tab = st.selectbox("Table", ["signals","trades","account_history","daily_summary"])
    try:
        conn = sqlite3.connect(DB_PATH)
        df_db = pd.read_sql(f"SELECT * FROM {db_tab} ORDER BY id DESC LIMIT 100", conn)
        conn.close()
        st.dataframe(df_db, use_container_width=True, hide_index=True)
        st.download_button(f"⬇ Export {db_tab}.csv", df_db.to_csv(index=False),
                            f"{db_tab}.csv", "text/csv")
    except Exception as e:
        st.warning(f"Database read error: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# AUTO-SCAN LOOP (triggered on each rerun while bot is running)
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["bot_running"] and selected_pairs:
    last = st.session_state.get("last_scan")
    run_now = True
    if last:
        try:
            last_dt = datetime.strptime(last, "%H:%M:%S").replace(
                year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
            run_now = (datetime.now() - last_dt).total_seconds() >= scan_interval
        except Exception:
            run_now = True

    if run_now:
        run_scan_cycle(selected_pairs, timeframe,
                       st.session_state["account_balance"],
                       risk_pct, lot_size, int(max_trades), daily_loss)

    # Auto-rerun to keep scanning
    time.sleep(1)
    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#333;font-size:0.72rem;font-family:monospace;padding:8px 0">
    AI SCANNER · Emevine Trading System · SMC / ICT / Price Action
    &nbsp;|&nbsp; ⚠️ Trading involves significant risk. This software is for educational purposes.
</div>
""", unsafe_allow_html=True)
