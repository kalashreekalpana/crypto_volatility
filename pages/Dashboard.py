import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Dashboard | Crypto Risk Analyzer",
    layout="wide"
)

# ---------------- LOGIN CHECK ----------------
if "logged_in" not in st.session_state:
    st.error("❌ Please login first")
    st.stop()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}

/* Cards */
.card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    height: 160px;
}
.card h4 {
    color: #58a6ff;
}

/* Start Analyzing Button */
div.stButton > button {
    background-color: #1f6feb;
    color: white;
    border-radius: 10px;
    padding: 12px 20px;
    font-size: 18px;
    font-weight: 600;
    border: none;
}
div.stButton > button:hover {
    background-color: #388bfd;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center;color:#58a6ff;'>🚀 Crypto Volatility & Risk Analyzer</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>📊 Analyzing cryptocurrency risk through advanced data analytics</p>",
    unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------- FEATURE CARDS ----------------
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class='card'>
        <h4>⚠️ Automated Risk</h4>
        <p>Detect volatility & market risk.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class='card'>
        <h4>⏱️ Real-Time Data</h4>
        <p>Live crypto prices from APIs.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class='card'>
        <h4>📈 Visual Charts</h4>
        <p>Interactive dashboards & trends.</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class='card'>
        <h4>😊 User Friendly</h4>
        <p>Simple & clean navigation.</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------- START ANALYZING BUTTON ----------------
st.markdown("<br><br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([3,2,3])
with col1:
    if st.button(" Start Analyzing"):
        st.switch_page("pages/data_acquisition.py")
with col2:
    if st.button("📊 Milestone 2: Data Processing"):
        st.switch_page("pages/Data_Processing.py")
