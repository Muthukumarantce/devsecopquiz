# myGUARD Streamlit Security Challenge

A Streamlit-based exhibition quiz inspired by the supplied DevSecOps/AI Agent prototype.

## Visitor flow
- Visitor answers 5 randomly selected questions from the active 30-question bank.
- Score is calculated automatically.
- **4/5 or 5/5:** visitor enters **Name only** (up to 25 characters) and receives a personalized **myGUARD Quiz Winner** badge.
- The winner badge keeps the supplied artwork and uses a large bold condensed display name beneath the gold `QUIZ WINNER` ribbon, with matching navy/gold styling and star/line ornaments. The name is dynamically scaled to keep even 25-character names readable, while retaining the same bold condensed Winner-style treatment.
- **0–3/5:** visitor is shown as a **Challenge Participant** and no winner badge is generated.

## Run
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
```

## Admin
Open **Admin** from the Streamlit sidebar. Set `ADMIN_PASSWORD` in `.streamlit/secrets.toml`.

Upload either CSV or XLSX with exactly these columns:
`id, category, difficulty, question, option_a, option_b, option_c, option_d, answer`

The active question bank must contain exactly 30 questions.

## Important production note
This starter uses local SQLite and a local question CSV for easy setup. For a public exhibition deployment, use a persistent database such as PostgreSQL/Supabase and keep the answer key server-side rather than in a publicly accessible app asset.
