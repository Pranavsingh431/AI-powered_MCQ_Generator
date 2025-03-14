import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcq_generator.utils import read_file,get_table_data
from src.mcq_generator.logger import logging
#imporing necessary packages packages from langchain
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain


# Load environment variables from the .env file
load_dotenv()

# Access the environment variables just like you would with os.environ
os.getenv("GOOGLE_API_KEY")
if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("GOOGLE_API_KEY is not set in environment!")

llm = GoogleGenerativeAI(model='gemini-2.0-pro-exp-02-05')

template="""
Text:{text}
You are an expert MCQ maker. Given the above text, it is your job to \
create a quiz  of {number} multiple choice questions in {tone} tone. 
Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like  RESPONSE_JSON below  and use it as a guide. \
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}

"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "tone", "response_json"],
    template=template)


quiz_chain=LLMChain(llm=llm,prompts=quiz_generation_prompt,output_key="quiz",verbose=True)


template2="""
You are an expert english grammarian and writer. Given a Multiple Choice Quiz.\
You need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity analysis. 
if the quiz is not at per with the cognitive and analytical abilities of the students,\
update the quiz questions which needs to be changed and change the tone such that it perfectly fits the student abilities
Quiz_MCQs:
{quiz}

Check from an expert English Writer of the above quiz:
"""


quiz_evaluation_prompt=PromptTemplate(input_variables=["quiz"], template=template2)

review_chain=LLMChain(llm=llm, prompt=quiz_evaluation_prompt, output_key="review", verbose=True)


# This is an Overall Chain where we run the two chains in Sequence
generate_evaluate_chain=SequentialChain(chains=[quiz_chain, review_chain], input_variables=["text", "number", "subject", "tone", "response_json"],
                                        output_variables=["quiz", "review"], verbose=True,)