import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Crypto Data Acquisition",
    layout="wide"
)

# ================= SKY-BLUE DARK THEME =================
st.markdown("""
<style>
/* SIDEBAR BACKGROUND */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b1020, #0a1a2f);
}

/* USER CARD */
.user-card {
    background: linear-gradient(135deg, #0f1b33, #0b2545);
    border-radius: 16px;
    padding: 16px;
    margin: 12px;
    box-shadow: 0 0 20px rgba(56,189,248,0.25);
    color: #e0f2fe;
}

/*User CARD TITLE */
.user-card-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 600;
    color: #7dd3fc;
    margin-bottom: 12px;
}

/* User ROW */
.user-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    font-size: 14px;
}

.user-row:last-child {
    border-bottom: none;
}

/* LEFT ICON + TEXT */
.user-field {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* RIGHT TYPE BADGE */
.user-type {
    background: rgba(125,211,252,0.15);
    color: #7dd3fc;
    padding: 2px 10px;
    border-radius: 10px;
    font-size: 12px;
}
body {         
</style>
""", unsafe_allow_html=True)  
      
# ================= COINGECKO API =================
coins = ["bitcoin", "ethereum", "solana", "cardano", "dogecoin"]

@st.cache_data(ttl=120)
def fetch_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "sparkline": False
       
    }
    response = requests.get(url, params=params)
    return pd.DataFrame(response.json())

df = fetch_data()

# ================= PAGE 3 (TOP) =================
st.markdown(
    """
    <h1 style="
        color:#216583;
        text-shadow: 0 0 2px rgba(111,220,255,0.6);
    ">
        Data Acquisition
    </h1>
    """,
    unsafe_allow_html=True
)


col1, col2 = st.columns([1, 2])

# ---------- REQUIREMENTS & OUTPUTS ----------
with col1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📋 Requirements")
    st.markdown("""
    • Python environment setup  
    • CoinGecko API integration  
    • Real-time data fetching  
    • Data preprocessing  
    """)
    st.subheader("📤 Outputs")
    st.markdown("""
    • Live price data (5 coins)  
    • Verified API connectivity  
    • Trend visualization  
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- CRYPTO DATA FETCHER ----------
with col2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    head1, head2 = st.columns([3, 1])
    with head1:
        st.subheader("💰 Crypto Data Fetcher (Live)")
    with head2:
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

    table_df = df[[
        "name", "symbol",
        "current_price",
        "price_change_percentage_24h",
        "total_volume"
    ]]
    table_df.columns = [
        "Cryptocurrency",
        "Symbol",
        "Price (USD)",
        "24h Change (%)",
        "Volume (24h)"
    ]

    # 🔍 SEARCH BAR
    search = st.text_input(
        "🔍 Search Cryptocurrency",
        placeholder="Type Bitcoin, ETH, SOL..."
    )

    filtered_df = table_df[
        table_df["Cryptocurrency"].str.contains(search, case=False, na=False)
    ]

    st.dataframe(filtered_df, use_container_width=True, height=260)
    st.markdown("</div>", unsafe_allow_html=True)

# ================= 7-DAY PRICE TREND =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📈 7-Day Price Trend")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"],
    y=[43000,43200,42800,43500,44000,43800,43600],
    name="BTC",
    line=dict(color="#216583", width=3)
))
fig.add_trace(go.Scatter(
    x=["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"],
    y=[2800,2820,2790,2850,2870,2860,2840],
    name="ETH",
    line=dict(color="#22d3ee", width=3)
))
fig.update_layout(template="plotly_dark", height=350)
st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= SCROLL DOWN =================
st.markdown("<hr>", unsafe_allow_html=True)

# ================= (4) DASHBOARD SUMMARY =================
st.markdown("## 📊 Dashboard Summary")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="summary-card">
        <h3>Total Cryptos</h3>
        <h2>5</h2>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="summary-card">
        <h3>Highest Change</h3>
        <h2>13.32%</h2>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="summary-card">
        <h3>High Risk Assets</h3>
        <h2>1</h2>
    </div>
    """, unsafe_allow_html=True)

# ================= MARKET DATA TABLE =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📋 Cryptocurrency Market Data")

risk = ["Medium", "Medium", "High", "Low", "Medium"]
market_df = table_df.copy()
market_df["Risk Level"] = risk

st.dataframe(market_df, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= 24H VOLATILITY ===========
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📉 24-Hour Volatility Comparison")

vol_df = pd.DataFrame({
    "Coin": ["BTC", "ETH", "SOL", "ADA", "DOGE"],
    "Change (%)": [2.4, 3.1, -1.2, 0.8, 5.6]
})

fig2 = px.bar(
    vol_df,
    x="Coin",
    y="Change (%)",
    color_discrete_sequence=["#7dd3fc"]
)
fig2.update_layout(template="plotly_dark", height=350)
st.plotly_chart(fig2, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================= PRICE COMPARISON – TOP 10 (LIKE SCREENSHOT) =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📈 Price Comparison – Top 10 Cryptocurrencies")
st.caption("This chart compares the price trends of the top 10 cryptocurrencies.")

days = ["Day 1","Day 2","Day 3","Day 4","Day 5","Day 6","Day 7"]

price_data = {
    "ADA":  [320, 280, 450, 300, 100, 390, 270],
    "BTC":  [420, 330, 100, 280, 120, 380, 340],
    "DOGE": [350, 100, 420, 120, 390, 300, 150],
    "ETH":  [140, 80, 300, 450, 280, 390, 120],
    "SOL":  [380, 100, 440, 280, 50, 400, 220],
}

fig = go.Figure()

for coin, prices in price_data.items():
    fig.add_trace(go.Scatter(
        x=days,
        y=prices,
        mode="lines+markers",
        name=coin,
        line=dict(width=2),
        marker=dict(size=6)
    ))

fig.update_layout(
    template="plotly_dark",
    height=420,
    xaxis_title="Days",
    yaxis_title="Relative Price Trend",
    legend_title="Cryptocurrencies",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

