import streamlit as st
import sqlite3
import hashlib
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Login | Crypto Volatility & Risk Analyzer",
    layout="centered"
)

# ---------------- DATABASE ----------------
conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password_hash TEXT,
    created_at TEXT
)
""")
conn.commit()

# ---------------- FUNCTIONS ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password):
    try:
        cursor.execute(
            "INSERT INTO user (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), datetime.now())
        )
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    cursor.execute(
        "SELECT * FROM user WHERE username=? AND password_hash=?",
        (username, hash_password(password))
    )
    return cursor.fetchone()

# ---------------- UI ----------------
st.title("🔐 Login to Crypto Volatility & Risk Analyzer")

tab1, tab2 = st.tabs(["Login", "Register"])

# ---------------- LOGIN ----------------
with tab1:
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.success("✅ Login Successful")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.switch_page("pages/dashboard.py")
        else:
            st.error("❌ Invalid Username or Password")

# ---------------- REGISTER ----------------
with tab2:
    st.subheader("Create New Account")

    reg_username = st.text_input("Username", key="reg_user")
    reg_email = st.text_input("Email")
    reg_password = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Register"):
        if register_user(reg_username, reg_email, reg_password):
            st.success("🎉 Registration Successful! Please login.")
        else:
            st.error("⚠️ Username already exists")
