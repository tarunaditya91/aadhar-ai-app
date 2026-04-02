import cv2
import pytesseract
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_URL = os.getenv("DB_URL")


# 👉 IMPORTANT (Mac fix - ensure tesseract path)
pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"

# 👉 Change this path to your image
image_path = "image copy 3.png"

# Read image
img = cv2.imread(image_path)

# Check if image loaded
if img is None:
    print("❌ Error: Image not found. Check file path.")
    exit()

# Convert to grayscale (improves OCR)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply threshold (improves text clarity)
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# OCR extraction
ocr_text = pytesseract.image_to_string(thresh)

print("✅ OCR OUTPUT:\n")
print(ocr_text)


def build_prompt(text):
    return f"""
Extract Aadhaar details from the text below.

Return ONLY JSON in this format:
{{
  "name": "",
  "dob": "",
  "aadhaar": "",
  "gender": ""
}}
Return ONLY JSON.
Do not add explanation.
Do not use ```json.

Text:
{text}
"""

def call_llm(prompt):
    from groq import Groq

    client = Groq(api_key=GROQ_API_KEY)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content


import json

response = call_llm(build_prompt(ocr_text))

data = json.loads(response)

print(data)





print(type(data))

data["aadhaar"] = data["aadhaar"].replace(" ", "")
print(data)

import psycopg2



def get_connection():
    return psycopg2.connect(DB_URL)

def check_aadhaar(aadhaar):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM aadhar_data WHERE aadhaar = %s",
        (aadhaar,)
    )

    result = cursor.fetchone()  # returns tuple
    conn.close()
    print("DB Result:", result)

    return result

def calculate_match_score(db_data, extracted_data):
    score = 0
    total = 4
    print(db_data[1].lower(),extracted_data["name"].lower())
    print(db_data[2],extracted_data["dob"])
    print(db_data[3].replace(" ", ""),extracted_data["aadhaar"].replace(" ", ""))
    print(db_data[4].lower(),extracted_data["gender"].lower())

    if db_data[1].lower() == extracted_data["name"].lower():
        # print(db_data[1].lower(),extracted_data["name"].lower())
        score += 1

    if db_data[2] == extracted_data["dob"]:
        # print(db_data[2],extracted_data["dob"])
        score += 1

    if db_data[3].replace(" ", "") == extracted_data["aadhaar"].replace(" ", ""):
        # print(db_data[3].replace(" ", ""),extracted_data["aadhaar"].replace(" ", ""))
        score += 1

    if db_data[4].lower() == extracted_data["gender"].lower(): 
        # print(db_data[4].lower(),extracted_data["gender"].lower())
        score += 1

    percentage = (score / total) * 100

    return score, percentage

# check DB
db_result = check_aadhaar(data["aadhaar"])

if db_result:
    score, percent = calculate_match_score(db_result, data)

    print("✅ Record found in DB")
    print("Score:", score)
    print("Match %:", percent)

else:
    print("❌ No record found in DB")