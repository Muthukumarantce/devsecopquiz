import io
from pathlib import Path
import pandas as pd
import streamlit as st
from quiz_engine import validate
from database import init_db, read_results

st.set_page_config(page_title="myGUARD Admin", page_icon="🛡️", layout="wide")
init_db()

# -----------------------------------------------------------------------------
# Admin authentication
# Configure in .streamlit/secrets.toml (local) or Streamlit Cloud Secrets:
# ADMIN_USERNAME = "admin"
# ADMIN_PASSWORD = "your-strong-password"
# -----------------------------------------------------------------------------
ADMIN_USERNAME = st.secrets.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "CHANGE-ME")

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False

st.title("🛡️ myGUARD — Admin")

if not st.session_state.admin_authenticated:
    st.subheader("Admin Login")
    st.caption("Enter the configured admin username and password to continue.")

    with st.form("admin_login", clear_on_submit=False):
        username = st.text_input("Admin username", placeholder="Enter username")
        password = st.text_input("Admin password", type="password", placeholder="Enter password")
        login = st.form_submit_button("🔐 Login", type="primary", use_container_width=True)

    if login:
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("Invalid admin username or password.")
    st.stop()

# -----------------------------------------------------------------------------
# Authenticated admin area
# -----------------------------------------------------------------------------
st.success(f"Authenticated as **{ADMIN_USERNAME}**")
if st.button("Log out", key="admin_logout"):
    st.session_state.admin_authenticated = False
    st.rerun()

st.header("Question Bank")
uploaded = st.file_uploader("Upload your 30-question bank", type=["csv", "xlsx"])
if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        errors = validate(df)
        if errors:
            for e in errors:
                st.error(e)
        else:
            st.success("Valid: exactly 30 questions.")
            st.dataframe(df, use_container_width=True)
            if st.button("Publish Question Bank", type="primary"):
                Path("data").mkdir(exist_ok=True)
                df.to_csv("data/questions.csv", index=False)
                st.cache_data.clear()
                st.success("Published. New quiz sessions use this bank.")
    except Exception as e:
        st.error(str(e))

st.header("Template")
template = pd.DataFrame(columns=[
    "id", "category", "difficulty", "question",
    "option_a", "option_b", "option_c", "option_d", "answer"
])
st.download_button(
    "Download CSV template",
    template.to_csv(index=False),
    "myguard_question_template.csv",
    "text/csv",
)

buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    template.to_excel(writer, index=False, sheet_name="Questions")
st.download_button(
    "Download XLSX template",
    buf.getvalue(),
    "myguard_question_template.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.header("Results")
rows = read_results()
if rows:
    df = pd.DataFrame(rows, columns=[
        "created_at", "name", "company", "industry", "score", "winner", "question_ids"
    ])
    a, b, c = st.columns(3)
    a.metric("Attempts", len(df))
    b.metric("Winners", int(df.winner.sum()))
    c.metric("Win Rate", f"{df.winner.mean() * 100:.1f}%")
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "Download results CSV",
        df.to_csv(index=False),
        "myguard_results.csv",
        "text/csv",
    )
else:
    st.info("No quiz attempts yet.")
