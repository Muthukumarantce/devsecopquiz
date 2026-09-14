import qrcode,sys
url=sys.argv[1] if len(sys.argv)>1 else "https://YOUR-REAL-STREAMLIT-URL"
qrcode.make(url).save("myguard_quiz_qr.png")
print("Created QR for",url)
