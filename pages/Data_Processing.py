"""
Milestone 2: Data Processing & Risk Metrics Dashboard
Streamlit page with volatility, Sharpe, Beta, rolling stats, and visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests

try:
    import yfinance as yf
    USE_YF = True
except ImportError:
    USE_YF = False

COINGECKO_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "ADA": "cardano", "DOGE": "dogecoin"}

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Data Processing", layout="wide")

# ================= LOGIN CHECK =================
if "logged_in" not in st.session_state:
    st.error("❌ Please login first")
    st.stop()

# ================= CONFIG =================
ASSETS = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD", "ADA": "ADA-USD", "DOGE": "DOGE-USD"}
BENCHMARK = "BTC"
TRADING_DAYS = 252
RISK_FREE_RATE = 0
WINDOW = 30

# ================= CUSTOM CSS =================
st.markdown("""
<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg, #1e293b, #0f172a); }
.main { background-color: #0f172a; }
.req-output-panel {
    background: linear-gradient(135deg, #1e3a5f, #0f2847);
    border-radius: 12px;
    padding: 20px;
    margin: 0 0 16px 0;
    border: 1px solid rgba(59,130,246,0.25);
    color: #f1f5f9;
}
.req-output-panel h4 {
    color: #60a5fa;
    font-size: 14px;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
    padding-bottom: 8px;
}
.req-output-panel ul {
    margin: 0;
    padding-left: 20px;
    font-size: 13px;
    line-height: 1.8;
}
</style>
""", unsafe_allow_html=True)

# ================= DATA FETCHING =================
def _fetch_coingecko(days):
    series_list = {}
    for sym, cg_id in COINGECKO_IDS.items():
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/coins/{cg_id}/market_chart",
                            params={"vs_currency": "usd", "days": min(days, 365)}, timeout=15)
            if r.status_code != 200:
                continue
            d = r.json()
            if "prices" not in d:
                continue
            df = pd.DataFrame(d["prices"], columns=["ts", "price"])
            df["date"] = pd.to_datetime(df["ts"], unit="ms").dt.normalize()
            series_list[sym] = df.groupby("date")["price"].last()
        except Exception:
            pass
    if not series_list:
        return pd.DataFrame()
    prices = pd.DataFrame(series_list).ffill().bfill().dropna()
    prices.index = pd.to_datetime(prices.index)
    return prices.sort_index()

@st.cache_data(ttl=3600)
def fetch_prices(days):
    prices = pd.DataFrame()
    if USE_YF:
        try:
            end = datetime.now()
            start = end - timedelta(days=days)
            for sym, ticker in ASSETS.items():
                try:
                    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
                    if not data.empty:
                        close = data["Close"]
                        if isinstance(close, pd.DataFrame):
                            close = close.iloc[:, 0]
                        prices[sym] = close
                except Exception:
                    pass
            prices = prices.dropna(how="all")
        except Exception:
            pass
    if prices.empty or len(prices) < 30:
        prices = _fetch_coingecko(days)
    if not prices.empty:
        prices = prices.ffill().bfill().dropna()
        prices.index = pd.to_datetime(prices.index)
    return prices.sort_index() if not prices.empty else pd.DataFrame()

def log_returns(prices):
    return np.log(prices / prices.shift(1)).dropna()

def volatility(returns):
    daily = returns.std()
    annual = daily * np.sqrt(TRADING_DAYS) * 100
    return annual

def sharpe_ratio(returns):
    return (returns.mean() - RISK_FREE_RATE) / returns.std().replace(0, np.nan)

def beta(returns):
    market = returns[BENCHMARK]
    var_m = market.var()
    return pd.Series({c: returns[c].cov(market) / var_m for c in returns.columns})

def var_95(returns):
    return returns.quantile(0.05) * 100

# ================= UI =================
st.markdown("""
<h1 style="color:#1e40af; font-weight:600;">
    📊 Data Processing
</h1>
""", unsafe_allow_html=True)

# Timeframe selector
col_top1, col_top2, col_top3 = st.columns([1, 1, 2])
with col_top1:
    timeframe = st.radio("Timeframe", ["30D", "90D", "1Y"], horizontal=True)
with col_top2:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

days_map = {"30D": 30, "90D": 90, "1Y": 365}
days = days_map.get(timeframe, 365)

# Fetch data
prices_df = fetch_prices(days)
if prices_df.empty:
    st.error("Could not fetch data. Please try again.")
    st.stop()

returns_df = log_returns(prices_df)

# Compute metrics
annual_vol = volatility(returns_df)
sharpe = sharpe_ratio(returns_df)
beta_vals = beta(returns_df)
var_vals = var_95(returns_df)

# -------- Two-column layout: Requirements/Outputs (left) | Dashboard (right) --------
col_left, col_right = st.columns([1, 3])

with col_left:
    st.markdown("""
    <div class="req-output-panel">
        <h4>📋 Requirements</h4>
        <ul>
            <li>Daily log-return calculation</li>
            <li>Statistical measures: volatility, Sharpe ratio, Beta</li>
            <li>Moving average & rolling volatility</li>
        </ul>
    </div>
    <div class="req-output-panel">
        <h4>📤 Outputs</h4>
        <ul>
            <li>Metrics table with risk indicators</li>
            <li>Processed dataset for visualization & classification</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("### Risk Metrics Dashboard Live Analysis")
    metrics_df = pd.DataFrame({
        "Crypto": ["BITCOIN", "ETHEREUM", "SOLANA", "CARDANO", "DOGECOIN"],
        "Volatility": [f"{round(annual_vol.get(c, 0), 2)}%" for c in ["BTC", "ETH", "SOL", "ADA", "DOGE"]],
        "Sharpe": [round(sharpe.get(c, 0), 2) for c in ["BTC", "ETH", "SOL", "ADA", "DOGE"]],
        "Beta": [round(beta_vals.get(c, 0), 2) for c in ["BTC", "ETH", "SOL", "ADA", "DOGE"]],
        "VaR": [f"{round(var_vals.get(c, 0), 2)}%" for c in ["BTC", "ETH", "SOL", "ADA", "DOGE"]]
    })

    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Volatility Comparison (Bar Chart)")
        vol_pct = [round(annual_vol.get(c, 0), 2) for c in ["BTC", "ETH", "SOL", "ADA", "DOGE"]]
        vol_df = pd.DataFrame({
            "Crypto": ["BITCOIN", "ETHEREUM", "SOLANA", "CARDANO", "DOGECOIN"],
            "Volatility (%)": vol_pct
        })
        fig_bar = px.bar(vol_df, x="Crypto", y="Volatility (%)", color="Volatility (%)",
                         color_continuous_scale="Viridis", text="Volatility (%)")
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bar.update_layout(template="plotly_dark", height=400, showlegend=False,
                             xaxis_tickangle=-45, margin=dict(b=80))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.markdown("#### 📈 Rolling Volatility Over Time (Line Chart)")
        rolling_vol = returns_df.rolling(WINDOW).std() * np.sqrt(TRADING_DAYS) * 100
        fig_line = go.Figure()
        for c in rolling_vol.columns:
            fig_line.add_trace(go.Scatter(x=rolling_vol.index, y=rolling_vol[c], name=c, mode='lines'))
        fig_line.update_layout(template="plotly_dark", height=400, xaxis_title="Date",
                              yaxis_title="Rolling Volatility (Annualized %)",
                              hovermode="x unified", legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_line, use_container_width=True)

    # 30-day Moving Average
    st.markdown("#### 📉 30-Day Moving Average (Price Trends)")
    ma_df = prices_df.rolling(WINDOW).mean()
    fig_ma = go.Figure()
    for c in ma_df.columns:
        fig_ma.add_trace(go.Scatter(x=ma_df.index, y=ma_df[c], name=c, mode='lines'))
    fig_ma.update_layout(template="plotly_dark", height=350, xaxis_title="Date",
                         yaxis_title="Price (USD)", hovermode="x unified")
    st.plotly_chart(fig_ma, use_container_width=True)

    # Part F: Interpretation
    st.markdown("---")
    st.markdown("### 📝 Interpretation & Inference")

    most_vol = annual_vol.idxmax()
    best_sharpe = sharpe.idxmax()

    st.markdown(f"""
- **Most volatile cryptocurrency:** {most_vol} ({annual_vol[most_vol]:.2f}% annualized volatility)
- **Best risk-adjusted return (Sharpe):** {best_sharpe} (Sharpe = {sharpe[best_sharpe]:.3f})
- **Beta interpretation:** Higher Beta indicates greater sensitivity to BTC market moves.
- **Investor suitability:** Lower volatility assets (e.g., BTC) suit conservative investors; higher Beta assets suit aggressive investors seeking amplified market exposure.
""")

    # Processed data preview
    with st.expander("📂 Processed Returns (First 10 rows)"):
        st.dataframe(returns_df.head(10).round(6), use_container_width=True, hide_index=True)

st.caption(f"Last updated: {datetime.now().strftime('%H-%M-%S')}")
