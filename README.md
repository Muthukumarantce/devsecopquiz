# myGUARD Security Challenge — Streamlit

## Visitor experience
- 5 random questions selected from the 30-question bank.
- 5-minute challenge.
- **5/5 = Quiz Winner** and gets a personalized gold Winner badge.
- **0/5 through 4/5 = Challenge Participant** and gets a personalized blue Participant badge.
- Visitor enters **name only**, maximum 25 characters.
- Both badges can be downloaded from the result screen.

## Admin login
Create `.streamlit/secrets.toml` locally or use Streamlit Cloud App Settings → Secrets:

```toml
ADMIN_USERNAME = "myguardadmin"
ADMIN_PASSWORD = "replace-with-a-strong-password"
```

Never commit `secrets.toml` to GitHub.

## Admin features
- Username + password login.
- Upload/validate/publish 30-question CSV/XLSX bank.
- Download CSV/XLSX templates.
- Results dashboard and CSV export.
- Built-in QR Code Generator: enter the final deployed quiz URL, generate, preview and download the PNG.

There is also a command-line helper:

```bash
python generate_qr.py https://your-app-name.streamlit.app
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deployment note
For Streamlit Community Cloud, push the project to GitHub and configure `ADMIN_USERNAME` and `ADMIN_PASSWORD` in the app's Secrets. The local SQLite database and local question-bank file are suitable for a starter/demo; for a public exhibition with multiple devices, use a persistent hosted database such as PostgreSQL/Supabase and server-side answer storage.
