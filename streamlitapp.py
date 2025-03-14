import streamlit as st
import os
import json
from dotenv import load_dotenv
from src.mcq_generator.utils import read_file, get_table_data

from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY is not set in environment!")
    st.stop()

# Initialize the language model
llm = GoogleGenerativeAI(model='gemini-2.0-pro-exp-02-05')

# MCQ Generation Prompt
quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "tone"],
    template="""
Text:{text}
You are an expert MCQ maker. Given the above text, create {number} multiple choice questions in {tone} tone.
Ensure the questions are well-structured and based on the provided text.
Format response as JSON like this:
{{ "1": {{ "mcq": "Question?", "options": {{ "a": "Option 1", "b": "Option 2", "c": "Option 3", "d": "Option 4" }}, "correct": "a" }} }}
    """
)
quiz_chain = LLMChain(llm=llm, prompt=quiz_generation_prompt, output_key="quiz", verbose=True)

# Chain Execution
generate_chain = SequentialChain(
    chains=[quiz_chain],
    input_variables=["text", "number", "tone"],
    output_variables=["quiz"],
    verbose=True,
)

# Streamlit UI
st.title("📝 AI-Powered MCQ Test")

# Choose between File Upload or Custom Prompt
generation_mode = st.radio(
    "Choose how you want to generate MCQs:",
    ["Upload a File", "Write a Prompt"],
    index=0
)

# File Upload Mode
if generation_mode == "Upload a File":
    uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

# Custom Prompt Mode
else:
    custom_prompt = st.text_area("Enter your topic or custom prompt:", "")

# Common Settings
num_mcqs = st.number_input("Number of MCQs", min_value=1, max_value=20, value=5)
tone = st.selectbox("Tone of Questions", ["Easy", "Medium", "Difficult"], index=1)

if st.button("Generate MCQs"):
    if generation_mode == "Upload a File" and uploaded_file is None:
        st.error("❌ Please upload a file before generating MCQs.")
    elif generation_mode == "Write a Prompt" and not custom_prompt.strip():
        st.error("❌ Please enter a prompt before generating MCQs.")
    else:
        try:
            # Extract text from file or use custom prompt
            if generation_mode == "Upload a File":
                st.info("📄 Extracting text from file...")
                extracted_text = read_file(uploaded_file)
            else:
                st.info("✍️ Using your custom prompt to generate MCQs...")
                extracted_text = custom_prompt

            # Generate MCQs using `invoke()`
            result = generate_chain.invoke({
                "text": extracted_text,
                "number": num_mcqs,
                "tone": tone
            })

            # Validate AI response
            raw_quiz_response = result.get("quiz", "").strip()
            if not raw_quiz_response:
                raise ValueError("AI model did not return valid MCQs. Please try again with different input.")

            # Clean AI response
            cleaned_quiz_response = raw_quiz_response.strip("```").replace("json", "").strip()

            # Convert AI output to structured format
            quiz_data = get_table_data(cleaned_quiz_response)
            if not quiz_data:
                raise ValueError("Error processing the AI response. The quiz format may be incorrect.")

            # Store quiz data in session state
            st.session_state.quiz_data = quiz_data
            st.session_state.quiz_submitted = False
            st.session_state.selected_answers = {}

            st.success("✅ MCQs Generated! Start the test below.")

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# If quiz data is stored in session state, show the quiz
if "quiz_data" in st.session_state and not st.session_state.quiz_submitted:
    st.subheader("🎯 Take the Test")

    selected_answers = {}
    quiz_data = st.session_state.quiz_data

    for idx, question in enumerate(quiz_data):
        st.write(f"**{idx+1}. {question['MCQ']}**")

        # Generate radio buttons for answer selection
        selected_answers[idx] = st.radio(
            f"Select your answer for question {idx+1}:",
            options=list(question["Choices"].split(" || ")),  
            key=f"q{idx}"
        )

    if st.button("Submit Answers"):
        st.session_state.quiz_submitted = True
        st.session_state.selected_answers = selected_answers

# Show Results After Submission
if "quiz_submitted" in st.session_state and st.session_state.quiz_submitted:
    st.subheader("📊 Test Results")

    correct_answers = 0
    quiz_data = st.session_state.quiz_data
    selected_answers = st.session_state.selected_answers

    for idx, question in enumerate(quiz_data):
        user_answer = selected_answers[idx].split("->")[0].strip()
        correct_answer = question["Correct"]

        if user_answer == correct_answer:
            st.success(f"✅ Q{idx+1}: Correct!")
            correct_answers += 1
        else:
            st.error(f"❌ Q{idx+1}: Incorrect! Correct answer: {correct_answer}")

    st.subheader(f"🏆 Your Score: {correct_answers} / {len(quiz_data)}")
