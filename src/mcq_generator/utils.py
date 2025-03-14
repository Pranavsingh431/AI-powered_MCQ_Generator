import PyPDF2
import pdfplumber
import json
import traceback
import io

def read_file(file):
    """Reads PDF or TXT file and extracts text."""
    file_extension = file.name.split(".")[-1].lower()

    if file_extension == "pdf":
        try:
            # First, try using PyPDF2
            pdf_reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() or "" for page in pdf_reader.pages])

            # If PyPDF2 fails, try pdfplumber
            if not text.strip():
                file.seek(0)  # Reset file pointer
                with pdfplumber.open(io.BytesIO(file.read())) as pdf:
                    text = "\n".join([page.extract_text() or "" for page in pdf.pages])

            if not text.strip():
                raise Exception("No extractable text found in the PDF. Try using an OCR tool.")

            return text.strip()

        except Exception as e:
            raise Exception(f"Error reading the PDF file: {str(e)}")

    elif file_extension == "txt":
        return file.read().decode("utf-8").strip()

    else:
        raise Exception("Unsupported file format! Only PDF and text files are supported.")

import json
import traceback

import json
import traceback

def get_table_data(quiz_str):
    """Converts AI-generated MCQ JSON string into a structured table format for Streamlit."""
    try:
        # Ensure quiz_str is not empty
        if not quiz_str or not quiz_str.strip():
            raise ValueError("Received empty response from the AI model.")

        # Remove ```json and ``` if present
        quiz_str = quiz_str.strip().strip("```").replace("json", "").strip()

        # Try loading JSON
        try:
            quiz_dict = json.loads(quiz_str)
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format received: {quiz_str[:500]}...")  # Show part of the response for debugging

        quiz_table_data = [
            {
                "MCQ": value["mcq"],
                "Choices": " || ".join([f"{option}-> {option_value}" for option, option_value in value["options"].items()]),
                "Correct": value["correct"]
            }
            for key, value in quiz_dict.items()
        ]
        return quiz_table_data

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return False


