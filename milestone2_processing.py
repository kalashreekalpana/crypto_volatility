"""
Milestone 2: Data Processing and Calculation
Crypto Volatility & Risk Analysis
Assets: BTC, ETH, SOL, ADA, DOGE | Benchmark: BTC
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend (no display needed)
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

try:
    import yfinance as yf
    USE_YFINANCE = True
except ImportError:
    USE_YFINANCE = False

import requests

# ==================== CONFIG ====================
ASSETS = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "ADA": "ADA-USD", "DOGE": "DOGE-USD"}
COINGECKO_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "ADA": "cardano", "DOGE": "dogecoin"}
BENCHMARK = "BTC"
TRADING_DAYS = 252
RISK_FREE_RATE = 0
WINDOW = 30

# ==================== PART A: DATA PREPARATION ====================
def _fetch_yfinance(days):
    """Fetch data via yfinance."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    series_list = {}
    for symbol, ticker in ASSETS.items():
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True, threads=False)
            if not data.empty and "Close" in data.columns:
                close = data["Close"]
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
                series_list[symbol] = close
        except Exception:
            pass
    if not series_list:
        return pd.DataFrame()
    prices_df = pd.DataFrame(series_list)
    return prices_df.dropna(how="all")

def _fetch_coingecko(days):
    """Fallback: fetch data via CoinGecko API (no local file writes)."""
    series_list = {}
    for symbol, cg_id in COINGECKO_IDS.items():
        try:
            url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart"
            resp = requests.get(url, params={"vs_currency": "usd", "days": min(days, 365)}, timeout=15)
            if resp.status_code != 200:
                continue
            data = resp.json()
            if "prices" not in data:
                continue
            df = pd.DataFrame(data["prices"], columns=["ts", "price"])
            df["date"] = pd.to_datetime(df["ts"], unit="ms").dt.normalize()
            s = df.groupby("date")["price"].last()
            series_list[symbol] = s
        except Exception:
            pass
    if not series_list:
        return pd.DataFrame()
    prices_df = pd.DataFrame(series_list)
    prices_df = prices_df.ffill().bfill().dropna()
    prices_df.index = pd.to_datetime(prices_df.index)
    return prices_df.sort_index()

def fetch_and_prepare_data(days=365):
    """Fetch historical daily closing prices and prepare clean dataset."""
    prices_df = pd.DataFrame()
    if USE_YFINANCE:
        try:
            prices_df = _fetch_yfinance(days)
        except Exception:
            pass
    if prices_df.empty or len(prices_df) < 30:
        prices_df = _fetch_coingecko(days)
    if prices_df.empty:
        raise RuntimeError("Could not fetch data. Check internet connection.")
    prices_df = prices_df.ffill().bfill().dropna()
    prices_df.index = pd.to_datetime(prices_df.index)
    return prices_df.sort_index()

# ==================== PART B: DAILY RETURNS (LOG RETURNS) ====================
def calculate_log_returns(prices_df):
    """Calculate daily logarithmic returns: r_t = ln(P_t / P_{t-1})"""
    returns_df = np.log(prices_df / prices_df.shift(1)).dropna()
    return returns_df

# ==================== PART C: STATISTICAL MEASURES ====================
def calculate_volatility(returns_df):
    """Daily volatility = std of returns. Annualized = daily * sqrt(252)"""
    daily_vol = returns_df.std()
    annual_vol = daily_vol * np.sqrt(TRADING_DAYS)
    return daily_vol, annual_vol

def calculate_sharpe_ratio(returns_df, rf=RISK_FREE_RATE):
    """Sharpe Ratio = (R_p - R_f) / sigma_p"""
    mean_return = returns_df.mean()
    std_return = returns_df.std()
    sharpe = (mean_return - rf) / std_return.replace(0, np.nan)
    return sharpe

def calculate_beta(returns_df, benchmark=BENCHMARK):
    """Beta = Cov(R_i, R_m) / Var(R_m). Benchmark = BTC"""
    if benchmark not in returns_df.columns:
        raise ValueError(f"Benchmark {benchmark} not in returns")
    
    market_returns = returns_df[benchmark]
    var_market = market_returns.var()
    
    betas = {}
    for col in returns_df.columns:
        cov = returns_df[col].cov(market_returns)
        betas[col] = cov / var_market if var_market != 0 else np.nan
    return pd.Series(betas)

def calculate_var(returns_df, confidence=0.95):
    """Value at Risk (VaR) - percentage loss at given confidence"""
    return returns_df.quantile(1 - confidence)

# ==================== PART D: MOVING AVERAGE & ROLLING VOLATILITY ====================
def calculate_moving_avg_rolling_vol(prices_df, returns_df, window=WINDOW):
    """30-day moving average and 30-day rolling volatility"""
    ma_df = prices_df.rolling(window=window).mean()
    rolling_vol_df = returns_df.rolling(window=window).std() * np.sqrt(TRADING_DAYS) * 100  # Annualized %
    return ma_df, rolling_vol_df

# ==================== MAIN EXECUTION ====================
def run_milestone2(days=365, save_csv=True):
    print("=" * 60)
    print("MILESTONE 2: DATA PROCESSING AND CALCULATION")
    print("=" * 60)
    
    # Part A: Data Preparation
    print("\n--- Part A: Data Preparation ---")
    prices_df = fetch_and_prepare_data(days=days)
    if prices_df.empty:
        raise RuntimeError("No price data retrieved.")
    print(f"Dataset shape: {prices_df.shape}")
    print(f"Date range: {prices_df.index[0].date()} to {prices_df.index[-1].date()}")
    print("\nFirst 5 rows of price data:")
    print(prices_df.head())
    
    # Part B: Daily Returns
    print("\n--- Part B: Daily Log Returns ---")
    returns_df = calculate_log_returns(prices_df)
    print("First 5 rows of returns:")
    print(returns_df.head().round(6))
    
    # Part C: Statistical Measures
    print("\n--- Part C: Statistical Measures ---")
    daily_vol, annual_vol = calculate_volatility(returns_df)
    sharpe = calculate_sharpe_ratio(returns_df)
    beta = calculate_beta(returns_df)
    var_95 = calculate_var(returns_df, 0.95) * 100  # as percentage
    
    metrics_df = pd.DataFrame({
        "Daily Volatility": daily_vol,
        "Annualized Volatility (%)": annual_vol * 100,
        "Sharpe Ratio": sharpe,
        "Beta (vs BTC)": beta,
        "VaR 95% (%)": var_95
    })
    
    print("\nRisk Metrics Table:")
    print(metrics_df.round(4))
    
    # Part D: Moving Average & Rolling Volatility
    print("\n--- Part D: 30-Day Moving Average & Rolling Volatility ---")
    ma_df, rolling_vol_df = calculate_moving_avg_rolling_vol(prices_df, returns_df)
    print(f"30-day MA and Rolling Volatility computed (window={WINDOW})")
    
    # Part E: Visualization
    print("\n--- Part E: Generating Visualizations ---")
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Bar chart - Volatility comparison
    ax1 = axes[0, 0]
    annual_vol_pct = annual_vol * 100
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(annual_vol_pct)))
    bars = ax1.bar(annual_vol_pct.index, annual_vol_pct.values, color=colors)
    ax1.set_ylabel("Volatility (%)")
    ax1.set_title("Volatility Comparison - All Cryptocurrencies")
    ax1.tick_params(axis='x', rotation=45)
    for bar in bars:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
                 f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=9)
    
    # 2. Line chart - Rolling volatility over time
    ax2 = axes[0, 1]
    for col in rolling_vol_df.columns:
        ax2.plot(rolling_vol_df.index, rolling_vol_df[col], label=col, alpha=0.8)
    ax2.set_ylabel("Rolling Volatility (Annualized %)")
    ax2.set_xlabel("Date")
    ax2.set_title("30-Day Rolling Volatility Over Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. 30-day Moving Average
    ax3 = axes[1, 0]
    for col in ma_df.columns:
        ax3.plot(ma_df.index, ma_df[col], label=col, alpha=0.8)
    ax3.set_ylabel("Price (USD)")
    ax3.set_xlabel("Date")
    ax3.set_title("30-Day Moving Average - Price Trends")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Risk metrics summary table (as text)
    ax4 = axes[1, 1]
    ax4.axis('off')
    table_data = metrics_df.round(3).values
    table = ax4.table(cellText=table_data, colLabels=metrics_df.columns, rowLabels=metrics_df.index,
                     loc='center', cellLoc='center', colColours=['#4472C4']*5)
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.8)
    ax4.set_title("Risk Metrics Dashboard", fontsize=12, pad=20)
    
    plt.tight_layout()
    plt.savefig("milestone2_dashboard.png", dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: milestone2_dashboard.png")
    
    # Part F: Interpretation
    print("\n" + "=" * 60)
    print("PART F: INTERPRETATION AND INFERENCE")
    print("=" * 60)
    
    most_volatile = annual_vol.idxmax()
    best_sharpe = sharpe.idxmax()
    
    print(f"\n1. Most Volatile Cryptocurrency: {most_volatile} ({annual_vol[most_volatile]*100:.2f}%)")
    print(f"2. Best Risk-Adjusted Return (Sharpe): {best_sharpe} (Sharpe = {sharpe[best_sharpe]:.3f})")
    print("\n3. Beta Interpretation (sensitivity to BTC market):")
    for coin, b in beta.items():
        if b > 1:
            interp = "More volatile than market"
        elif b < 1:
            interp = "Less volatile than market"
        else:
            interp = "Moves with market"
        print(f"   - {coin}: Beta = {b:.2f} -> {interp}")
    
    print("\n4. Investor Suitability:")
    print("   - Low volatility (BTC): Conservative investors seeking stability")
    print("   - High Sharpe: Better risk-adjusted returns (if positive)")
    print("   - High Beta: Suitable for aggressive investors seeking amplified market exposure")
    
    # Save processed dataset
    if save_csv:
        returns_df.to_csv("processed_returns.csv")
        metrics_df.to_csv("risk_metrics_table.csv")
        prices_df.to_csv("cleaned_prices.csv")
        rolling_vol_df.to_csv("rolling_volatility.csv")
        print("\nSaved: processed_returns.csv, risk_metrics_table.csv, cleaned_prices.csv, rolling_volatility.csv")
    
    return prices_df, returns_df, metrics_df, ma_df, rolling_vol_df

if __name__ == "__main__":
    prices, returns, metrics, ma, rolling_vol = run_milestone2(days=365)
