import tkinter as tk
from tkinter import filedialog
import logging
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import cohere

# Setup basic logging
logging.basicConfig(level=logging.DEBUG)

# Set the paths for Tesseract and Poppler
pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR\tesseract.exe"
poppler_path = r"poppler-24.07.0\Library\bin"

# Initialize Cohere API client
co = cohere.Client('0VBE3VyqTeKVmbxEYE2t9sOEKroR4ZG11SrD6v6M')  # Replace with your actual Cohere API key

# Define the function to query the Cohere API
def query_cohere_api(text):
    query=" give me the all the text of Summary in bullted point"
    #query = "Please provide the summary of the pdf and bullet point format. Make this such all the necessary information like Coverages and limit included from the PDF is mentioned in the summary."
    combined_message = f"{query}\n\n{text}"
    try:
        response = co.chat(
            message=combined_message,
            model="command-r-plus",
            temperature=0.3
        )
        relevant_data = response.text if hasattr(response, 'text') else "No content available"
        return relevant_data
    except Exception as e:
        logging.error(f"API Request Error: {e}")
        return "Error"

# Define a function to extract text from PDF using OCR
def extract_text_from_pdf(pdf_path, max_pages=20):
    text = ""
    try:
        # Use PyPDF2 to extract text from the PDF
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            num_pages = min(max_pages, len(reader.pages))  # Limit to max_pages or total pages, whichever is smaller
            for page_num in range(num_pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    # If no text is extracted, use OCR
                    images = convert_from_path(pdf_path, poppler_path=poppler_path, first_page=page_num+1, last_page=page_num+1)
                    for image in images:
                        ocr_text = pytesseract.image_to_string(image)
                        text += ocr_text
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
    return text

# Define a function to handle file selection and processing
def select_and_process_pdf():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

    if file_path:
        logging.info(f"Processing file: {file_path}")
        all_text = extract_text_from_pdf(file_path)
        summary = query_cohere_api(all_text)
        #print("Document Summary:")
        print(summary)
    else:
        logging.error("No file selected. Exiting...")

# Run the function to select and process a PDF
select_and_process_pdf()
