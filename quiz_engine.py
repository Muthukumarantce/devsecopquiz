import random
from pathlib import Path
import pandas as pd

REQUIRED=["id","category","difficulty","question","option_a","option_b","option_c","option_d","answer"]

def normalize(df):
    df=df.copy();df.columns=[str(c).strip().lower().replace(" ","_") for c in df.columns];return df

def validate(df):
    df=normalize(df); errors=[]
    missing=[c for c in REQUIRED if c not in df.columns]
    if missing: errors.append("Missing columns: "+", ".join(missing)); return errors
    if len(df)!=30: errors.append(f"Exactly 30 questions required; found {len(df)}.")
    if df["id"].duplicated().any(): errors.append("Question IDs must be unique.")
    if df["answer"].astype(str).str.upper().isin(["A","B","C","D"]).eq(False).any(): errors.append("answer must be A, B, C or D.")
    for c in REQUIRED:
        if df[c].isna().any() or df[c].astype(str).str.strip().eq("").any(): errors.append(f"{c} contains blank values.")
    for i,r in df.iterrows():
        opts=[str(r[x]).strip().lower() for x in ["option_a","option_b","option_c","option_d"]]
        if len(set(opts))<4: errors.append(f"Row {i+2}: options must be distinct.")
    return errors

def load_questions(path):
    df=pd.read_csv(path)
    errors=validate(df)
    if errors: raise ValueError("; ".join(errors))
    return to_records(df)

def to_records(df):
    df=normalize(df); mp={"a":0,"b":1,"c":2,"d":3}
    out=[]
    for _,r in df.iterrows():
        out.append({"id":str(r.id),"category":str(r.category),"difficulty":str(r.difficulty),
                    "question":str(r.question),
                    "options":[str(r.option_a),str(r.option_b),str(r.option_c),str(r.option_d)],
                    "answer":mp[str(r.answer).lower().strip()]})
    return out

def pick_questions(bank,count=5):
    return random.sample(bank,count)

def calculate_score(questions,answers):
    return sum(a==q["answer"] for q,a in zip(questions,answers))
