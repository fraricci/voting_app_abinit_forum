import streamlit as st
import database

# Paths to data
QA_FILE = "qa_data/gold_qa_sample_100.json"
ANS1_FILE = "qa_data/rag_ans_sample_100_reranker_larger_kb.pkl"
ANS2_FILE = "qa_data/llm_flash_latest_ans_sample_100.pkl"

# Initialize database
database.ingest_data(QA_FILE, ANS1_FILE, ANS2_FILE)

st.title("LLM vs RAG")
st.subtitle("Pick the answer you prefer.")

# Function to load next question
def load_next_question():
    q_data = database.get_random_question_pair()
    st.session_state.current_question = q_data

# Initialize session state
if 'current_question' not in st.session_state:
    load_next_question()

# Display current question
q_id, q_text, answers = st.session_state.current_question

st.subheader("Question:")
st.write(q_text)

cols = st.columns(2)

# Display answers and voting buttons
for i, ans in enumerate(answers):
    # MongoDB returns _id (ObjectId), so convert to str for key
    ans_id = str(ans["_id"])
    ans_text = ans["text"]
    
    with cols[i]:
        st.subheader(f"Answer {i+1}")
        st.text_area(f"Answer {i+1}", value=ans_text, height=300, key=f"text_{ans_id}", disabled=True)
        if st.button(f"Vote for Answer {i+1}", key=f"vote_{ans_id}"):
            # Determine winner/loser
            winner_id = ans["_id"]
            loser_id = answers[1-i]["_id"]
            
            # Verify IDs exist in DB before recording
            if database.validate_vote(q_id, winner_id, loser_id):
                database.record_vote(q_id, winner_id, loser_id)
                st.success("Vote recorded!")
                load_next_question()
                st.rerun()
            else:
                st.error("Invalid vote data. Reloading question.")
                load_next_question()
                st.rerun()

if st.button("Skip Question"):
    load_next_question()
    st.rerun()
