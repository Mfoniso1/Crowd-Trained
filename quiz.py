import streamlit as st
import google.generativeai as genai

st.title("🤖 AI-Generated Quiz App")

# Get Gemini API key from secrets
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

def generate_quiz(topic):
    prompt = (
        f"Create 10 multiple-choice quiz questions about {topic}. "
        "For each question, provide 4 options and indicate the correct answer. "
        "Format as JSON: "
        "[{'question': ..., 'options': [...], 'answer': ...}, ...]"
    )
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    import json, re
    match = re.search(r"\[.*\]", response.text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            st.error("Could not parse quiz questions. Try again.")
            return []
    else:
        st.error("No quiz questions found. Try again.")
        return []

def explain_answer(question, answer, topic):
    prompt = (
        f"Explain why '{answer}' is the correct answer to the following question about {topic}: {question}"
    )
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

if "quiz" not in st.session_state:
    st.session_state.quiz = []
if "score" not in st.session_state:
    st.session_state.score = 0
if "q_idx" not in st.session_state:
    st.session_state.q_idx = 0
if "completed" not in st.session_state:
    st.session_state.completed = False
if "show_explanation" not in st.session_state:
    st.session_state.show_explanation = False
if "last_explanation" not in st.session_state:
    st.session_state.last_explanation = ""
if "last_correct" not in st.session_state:
    st.session_state.last_correct = False
if "last_user_answer" not in st.session_state:
    st.session_state.last_user_answer = ""

if not st.session_state.quiz:
    topic = st.text_input("Enter a quiz topic (e.g., Machine Learning):")
    if st.button("Generate Quiz") and topic.strip():
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(topic.strip())
        if quiz:
            st.session_state.quiz = quiz
            st.session_state.score = 0
            st.session_state.q_idx = 0
            st.session_state.completed = False
            st.session_state.show_explanation = False
            st.rerun()
else:
    quiz = st.session_state.quiz
    topic = st.text_input("Quiz topic:", value="", disabled=True)
    if not st.session_state.completed and st.session_state.q_idx < len(quiz):
        q = quiz[st.session_state.q_idx]
        st.subheader(f"Question {st.session_state.q_idx + 1}: {q['question']}")
        user_answer = st.radio("Choose your answer:", q["options"], key=st.session_state.q_idx)
        
        if not st.session_state.show_explanation:
            if st.button("Check Answer"):
                st.session_state.last_user_answer = user_answer
                st.session_state.last_correct = (user_answer == q["answer"])
                if st.session_state.last_correct:
                    st.session_state.score += 1
                    st.success("Correct!")
                else:
                    st.error(f"Wrong! The correct answer is: {q['answer']}")
                with st.spinner("Getting explanation..."):
                    st.session_state.last_explanation = explain_answer(q["question"], q["answer"], topic)
                st.session_state.show_explanation = True
                st.rerun()
        else:
            if st.session_state.last_correct:
                st.success("Correct!")
            else:
                st.error(f"Wrong! The correct answer is: {q['answer']}")
            st.info(f"**Explanation:** {st.session_state.last_explanation}")
            if st.button("Next Question"):
                st.session_state.q_idx += 1
                if st.session_state.q_idx >= len(quiz):
                    st.session_state.completed = True
                st.session_state.show_explanation = False
                st.session_state.last_explanation = ""
                st.session_state.last_correct = False
                st.session_state.last_user_answer = ""
                st.rerun()
    else:
        st.success(f"Quiz completed! Your score: {st.session_state.score} / {len(quiz)}")
        if st.button("Restart Quiz"):
            st.session_state.quiz = []
            st.session_state.score = 0
            st.session_state.q_idx = 0
            st.session_state.completed = False
            st.session_state.show_explanation = False
            st.session_state.last_explanation = ""
            st.session_state.last_correct = False
            st.session_state.last_user_answer = ""
            st.rerun()