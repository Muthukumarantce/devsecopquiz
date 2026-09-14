import sqlite3, json
from pathlib import Path
from datetime import datetime, timezone

DB=Path("data/myguard.db")

def conn():
    DB.parent.mkdir(exist_ok=True); return sqlite3.connect(DB)

def init_db():
    c=conn()
    c.execute("""CREATE TABLE IF NOT EXISTS attempts(
      attempt_id TEXT PRIMARY KEY, created_at TEXT, score INTEGER, winner INTEGER,
      question_ids TEXT, answers TEXT, name TEXT, company TEXT, industry TEXT)""")
    c.commit();c.close()

def save_attempt(attempt_id,score,question_ids,answers,winner):
    c=conn();c.execute("INSERT OR REPLACE INTO attempts VALUES(?,?,?,?,?,?,?,?,?)",
      (attempt_id,datetime.now(timezone.utc).isoformat(),score,int(winner),json.dumps(question_ids),json.dumps(answers),"","",""));c.commit();c.close()

def save_claim(attempt_id,name):
    c=conn();c.execute("UPDATE attempts SET name=?,company=?,industry=? WHERE attempt_id=?",
      (name.strip(),"","",attempt_id));c.commit();c.close()

def read_results():
    c=conn(); rows=c.execute("SELECT created_at,name,company,industry,score,winner,question_ids FROM attempts ORDER BY created_at DESC").fetchall();c.close();return rows
