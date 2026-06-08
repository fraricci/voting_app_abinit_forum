import streamlit as st
import database

# Paths to data
QA_FILE = "qa_data/gold_qa_sample_100.json"
ANS1_FILE = "qa_data/rag_ans_sample_100_reranker_larger_kb.pkl"
ANS2_FILE = "qa_data/llm_flash_latest_ans_sample_100.pkl"

# Initialize database
# database.ingest_data(QA_FILE, ANS1_FILE, ANS2_FILE)

st.title("LLM vs RAG")

# Custom CSS to set text area background to white
st.markdown(
    """
    <style>
    div[data-baseweb="textarea"] textarea {
        background-color: white !important;
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write("Please, read the following info before starting. You can fold this section if you do not need it.")

with st.expander("Help / Info", expanded=True):
    st.write("Rate the answer you prefer with Up.")
    st.write("If you identify some errors or the answer is measleding use the Down rate.")
    st.write("If both answers are correct/valid, rate both of them with Up")
    st.write("Please, focus on the content of the answer more than on the style.")
    st.write("Confirming the vote will pull another question automatically at random. Skip the question if you do not want to vote (e.g. not familiar with the topic of the question, already rated question,...)")
    st.write("Rate how many answers you want.")
    st.write("Notes: It is completely anonymous. You cannot go back to the voted questions for corrections. Also, since questions are shown at random and we are not tracking who's voting what, the same question can be shown multiple times.")
    st.write("Dataset: 100 questions randomly selected from the old Abinit forum.")


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

# Store votes in session state
if 'vote_selections' not in st.session_state:
    st.session_state.vote_selections = {}

# Display answers and voting buttons
for i, ans in enumerate(answers):
    # MongoDB returns _id (ObjectId), so convert to str for key
    ans_id = str(ans["_id"])
    ans_text = ans["text"]
    
    with cols[i]:
        st.text_area(f"Answer {i+1}", value=ans_text, height=300, key=f"text_{ans_id}", disabled=True)
        
        # Radio button for Up/Down
        # Use a list of options that starts with a blank or 'None' option to allow unselected.
        # But user wants to remove "Select". I can use None as a default, 
        # and hide it if possible, or use a custom format_func.
        
        # To remove 'Select', use an empty option for "No rating"
        options = [None, "Up (Good/Correct/Prefer)", "Down (Error/Misleading/Incomplete)"]
        
        selection = st.radio(
            f"Rate Answer {i+1}:",
            options=options,
            format_func=lambda x: "No rating" if x is None else x,
            key=f"radio_{ans_id}"
        )
        st.session_state.vote_selections[ans_id] = selection

if st.button("Confirm Vote"):
    # Allow partial votes: at least one answer must have an 'Up' or 'Down'
    votes_to_save = {ans_id: selection for ans_id, selection in st.session_state.vote_selections.items() if selection is not None}
    
    if not votes_to_save:
        st.error("Please rate at least one answer before confirming.")
    else:
        # Save votes
        database.record_vote(q_id, votes_to_save)
        st.success("Votes recorded!")
        # Clear selections and load next
        st.session_state.vote_selections = {}
        load_next_question()
        st.rerun()

if st.button("Skip Question"):
    st.session_state.vote_selections = {}
    load_next_question()
    st.rerun()
