import time, uuid
from pathlib import Path
import streamlit as st
from quiz_engine import load_questions, pick_questions, calculate_score
from database import init_db, save_attempt, save_claim
from badge_generator import generate_winner_badge, generate_participant_badge, MAX_NAME_CHARS

st.set_page_config(page_title="myGUARD Security Challenge", page_icon="🛡️", layout="centered")

init_db()
QUESTIONS_FILE = Path("data/questions.csv")

st.markdown("""<style>
.stApp{background:radial-gradient(circle at 20% -10%,#16222e 0%,#0f1720 45%);color:#e6edf3}
.block-container{max-width:600px;padding-top:2rem}
.brand{text-align:center;font-size:44px;font-weight:900;letter-spacing:-2px}.brand span{color:#2ecc87}
.pill{display:inline-block;padding:6px 12px;border-radius:20px;border:1px solid #2ecc87;color:#2ecc87;font-weight:800;font-size:12px}
.question{font-size:22px;font-weight:600;line-height:1.45;margin:18px 0}
div[data-testid="stRadio"] label{background:#0b121a;border:1px solid #263241;border-radius:10px;padding:10px 12px;margin-bottom:8px}
.winner{text-align:center;font-size:38px;font-weight:800;color:#ffb02e}.participant{text-align:center;font-size:32px;font-weight:800;color:#4d9fff}.score{text-align:center;font-size:64px;font-weight:700;color:#2ecc87}
</style>""", unsafe_allow_html=True)

for k,v in {"stage":"start","questions":[],"answers":[],"current":0,"started":None,"attempt_id":None,"score":None}.items():
    st.session_state.setdefault(k,v)

def bank():
    return load_questions(QUESTIONS_FILE)

def start_quiz():
    st.session_state.questions=pick_questions(bank(),5)
    st.session_state.answers=[None]*5
    st.session_state.current=0
    st.session_state.started=time.time()
    st.session_state.attempt_id=str(uuid.uuid4())
    st.session_state.stage="quiz"

def finish():
    score=calculate_score(st.session_state.questions,st.session_state.answers)
    st.session_state.score=score
    # Only a perfect 5/5 is a winner. 4/5 and below are participants.
    save_attempt(st.session_state.attempt_id,score,[q["id"] for q in st.session_state.questions],st.session_state.answers,score==5)
    st.session_state.stage="result"

st.markdown('<div class="brand">my<span>GUARD</span></div><div style="text-align:center"><span class="pill">ENGINEERING EXPO • SECURITY CHALLENGE</span></div>',unsafe_allow_html=True)

if st.session_state.stage=="start":
    st.markdown("###")
    st.markdown('<div style="text-align:center"><span style="color:#ffb02e">🏆 Score 5/5 to win the myGUARD Quiz Winner badge</span></div>',unsafe_allow_html=True)
    st.title("Think you can beat this in 5 questions?")
    st.write("You've just seen how it’s done. Now let's see if it stuck. 5 quick questions — just you, your instincts, and a score waiting at the end.")
    cols=st.columns(2); cols[0].metric("Challenge Questions","5"); cols[1].metric("Winner","5 / 5")
    if st.button("Take the challenge →",type="primary",use_container_width=True):
        start_quiz(); st.rerun()
    st.caption("AI agents • Security guardrails • CI/CD • Patches & versions")

elif st.session_state.stage=="quiz":
    elapsed=int(time.time()-st.session_state.started)
    remaining=max(0,300-elapsed)
    if remaining==0:
        finish(); st.rerun()
    q=st.session_state.questions[st.session_state.current]
    n=st.session_state.current+1
    st.progress(n/5,text=f"Question {n} of 5")
    st.caption(f"{q['difficulty']}  •  {q['category']}  •  Time remaining {remaining//60:02d}:{remaining%60:02d}")
    st.markdown(f'<div class="question">{q["question"]}</div>',unsafe_allow_html=True)
    previous=st.session_state.answers[st.session_state.current]
    options=q["options"]
    index=previous if previous is not None else None
    selected=st.radio("Answer",options,index=index,key=f"radio_{q['id']}",label_visibility="collapsed")
    if selected is not None: st.session_state.answers[st.session_state.current]=options.index(selected)
    c1,c2=st.columns(2)
    with c1:
        if n>1 and st.button("← Back",use_container_width=True):
            st.session_state.current-=1;st.rerun()
    with c2:
        if st.button("Finish" if n==5 else "Next →",type="primary",use_container_width=True):
            if st.session_state.answers[st.session_state.current] is None: st.error("Please select an answer.")
            elif n==5: finish();st.rerun()
            else: st.session_state.current+=1;st.rerun()

elif st.session_state.stage=="result":
    score=st.session_state.score
    is_winner = score == 5
    if is_winner:
        st.markdown(f'<div class="score">{score}<span style="font-size:22px;color:#7d8b99">/5</span></div><div class="winner">🏆 QUIZ WINNER!</div>',unsafe_allow_html=True)
        st.success("Perfect score! You qualified for the myGUARD Quiz Winner badge.")
        badge_title = "🎉 Your personalized myGUARD Quiz Winner badge"
        badge_generator = generate_winner_badge
        file_prefix = "myGUARD-Quiz-Winner"
        claim_message = "Badge claim recorded. Show this personalized badge to the stall team to collect your physical sticker."
    else:
        st.markdown(f'<div class="score">{score}<span style="font-size:22px;color:#7d8b99">/5</span></div><div class="participant">🎯 CHALLENGE PARTICIPANT</div>',unsafe_allow_html=True)
        st.info("Thanks for participating in the myGUARD Security Challenge! A score of 5/5 is required for the Quiz Winner badge. You can claim a personalized Challenge Participant badge.")
        badge_title = "🎯 Your personalized myGUARD Challenge Participant badge"
        badge_generator = generate_participant_badge
        file_prefix = "myGUARD-Challenge-Participant"
        claim_message = "Participant badge recorded. Show this personalized badge to the stall team."

    if st.session_state.get("claimed", False):
        st.markdown(f"### {badge_title}")
        badge_bytes = st.session_state.get("badge_bytes")
        if badge_bytes:
            st.image(badge_bytes, use_container_width=True)
            st.download_button(
                "⬇️ DOWNLOAD MY BADGE",
                data=badge_bytes,
                file_name=f"{file_prefix}-{st.session_state.get('claim_name','Participant').replace(' ', '-')}.jpg",
                mime="image/jpeg", use_container_width=True, type="primary",
            )
        st.success(claim_message)
    else:
        with st.form("claim"):
            name=st.text_input("Name *", placeholder="Enter your name", max_chars=MAX_NAME_CHARS, help=f"Maximum {MAX_NAME_CHARS} characters. Long names are automatically scaled to fit the badge.")
            ok=st.form_submit_button("GET MY BADGE",type="primary",use_container_width=True)
        if ok:
            clean=" ".join(name.strip().split())
            if not clean:
                st.error("Please enter your name.")
            elif len(clean)>MAX_NAME_CHARS:
                st.error(f"Name must be {MAX_NAME_CHARS} characters or fewer.")
            else:
                badge_bytes=badge_generator(clean)
                save_claim(st.session_state.attempt_id,clean)
                st.session_state.claimed=True
                st.session_state.claim_name=clean
                st.session_state.badge_bytes=badge_bytes
                st.rerun()
    if st.button("Try again",use_container_width=True):
        for key in ["claimed","score","questions","answers","current","started","attempt_id","claim_name","badge_bytes"]:
            st.session_state.pop(key,None)
        st.session_state.stage="start"
        st.rerun()
