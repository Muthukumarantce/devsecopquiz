import io
from pathlib import Path
import pandas as pd
import streamlit as st
import qrcode
from quiz_engine import validate
from database import init_db,read_results

st.set_page_config(page_title="myGUARD Admin",page_icon="🛡️",layout="wide")
init_db()
st.title("🛡️ myGUARD — Admin")

username = st.text_input("Admin username")
password = st.text_input("Admin password",type="password")
expected_user = st.secrets.get("ADMIN_USERNAME","admin")
expected_password = st.secrets.get("ADMIN_PASSWORD","CHANGE-ME")
if username != expected_user or password != expected_password:
    st.info("Enter the admin username and password to continue.")
    st.stop()

st.success(f"Authenticated as {expected_user}")

st.header("Question Bank")
uploaded=st.file_uploader("Upload your 30-question bank",type=["csv","xlsx"])
if uploaded:
    try:
        df=pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
        errors=validate(df)
        if errors:
            for e in errors: st.error(e)
        else:
            st.success("Valid: exactly 30 questions.")
            st.dataframe(df,use_container_width=True)
            if st.button("Publish Question Bank",type="primary"):
                Path("data").mkdir(exist_ok=True);df.to_csv("data/questions.csv",index=False)
                st.cache_data.clear();st.success("Published. New quiz sessions use this bank.")
    except Exception as e: st.error(str(e))

st.header("Template")
template=pd.DataFrame(columns=["id","category","difficulty","question","option_a","option_b","option_c","option_d","answer"])
st.download_button("Download CSV template",template.to_csv(index=False),"myguard_question_template.csv","text/csv")
buf=io.BytesIO()
with pd.ExcelWriter(buf,engine="openpyxl") as writer:
    template.to_excel(writer,index=False,sheet_name="Questions")
st.download_button("Download XLSX template",buf.getvalue(),"myguard_question_template.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.header("QR Code Generator")
st.write("Generate the QR code that visitors scan to open the quiz. Use your deployed Streamlit URL, then download the PNG for printing.")
quiz_url = st.text_input("Quiz URL", placeholder="https://your-app-name.streamlit.app")
if st.button("Generate QR Code", type="primary"):
    if not quiz_url.strip().startswith(("https://", "http://")):
        st.error("Please enter a valid URL starting with https:// or http://")
    else:
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=12, border=4)
        qr.add_data(quiz_url.strip()); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_bytes = io.BytesIO(); img.save(qr_bytes, format="PNG"); qr_bytes.seek(0)
        st.image(qr_bytes.getvalue(), width=320, caption="myGUARD Quiz QR Code")
        st.download_button("⬇️ DOWNLOAD QR CODE", data=qr_bytes.getvalue(), file_name="myguard_quiz_qr.png", mime="image/png", type="primary")
        st.success("QR generated. Test the downloaded QR with at least two phones before printing.")

st.header("Results")
rows=read_results()
if rows:
    df=pd.DataFrame(rows,columns=["created_at","name","company","industry","score","winner","question_ids"])
    a,b,c=st.columns(3);a.metric("Attempts",len(df));b.metric("Winners",int(df.winner.sum()));c.metric("Win Rate",f"{df.winner.mean()*100:.1f}%")
    st.dataframe(df,use_container_width=True)
    st.download_button("Download results CSV",df.to_csv(index=False),"myguard_results.csv","text/csv")
else: st.info("No quiz attempts yet.")
