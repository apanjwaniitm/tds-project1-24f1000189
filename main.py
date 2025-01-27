from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import subprocess
import os
import json
import sqlite3
from datetime import datetime
from fastapi.responses import PlainTextResponse
from openai import ChatCompletion

# Initialize FastAPI app
app = FastAPI()

# LLM helper function
def call_llm(prompt: str) -> str:
    """Call the LLM to process a given prompt."""
    response = ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()

# Endpoint: POST /run
@app.post("/run")
def run_task(task: str = Query(..., description="Plain-English task description")):
    try:
        # Step 1: Parse the task using LLM
        prompt = f"Analyze the task and break it into deterministic Python steps. Task: {task}"
        steps = call_llm(prompt)

        # Step 2: Execute the steps
        exec_locals = {}
        exec(steps, globals(), exec_locals)
        
        return {"status": "success", "message": "Task executed successfully."}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# Endpoint: GET /read
@app.get("/read", response_class=PlainTextResponse)
def read_file(path: str = Query(..., description="Path to the file to read")):
    try:
        if not os.path.exists(path):
            raise HTTPException(status_code=404, detail="File not found")
        with open(path, "r") as file:
            content = file.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

# Sample functions for operation tasks
def install_and_run_uv(user_email):
    subprocess.run(["pip", "install", "uv"], check=True)
    subprocess.run([
        "python", "datagen.py", user_email
    ], check=True)

def format_file_with_prettier(file_path):
    subprocess.run(["npx", "prettier@3.4.2", "--write", file_path], check=True)

def count_wednesdays(input_path, output_path):
    with open(input_path, "r") as file:
        dates = file.readlines()
    count = sum(1 for date in dates if datetime.strptime(date.strip(), "%Y-%m-%d").weekday() == 2)
    with open(output_path, "w") as file:
        file.write(str(count))

def sort_contacts(input_path, output_path):
    with open(input_path, "r") as file:
        contacts = json.load(file)
    sorted_contacts = sorted(contacts, key=lambda x: (x["last_name"], x["first_name"]))
    with open(output_path, "w") as file:
        json.dump(sorted_contacts, file, indent=2)

def extract_log_headlines(log_dir, output_path):
    log_files = sorted(
        [f for f in os.listdir(log_dir) if f.endswith(".log")],
        key=lambda x: os.path.getmtime(os.path.join(log_dir, x)), reverse=True
    )[:10]
    with open(output_path, "w") as output:
        for log_file in log_files:
            with open(os.path.join(log_dir, log_file), "r") as log:
                output.write(log.readline())

def index_markdown_titles(doc_dir, output_path):
    index = {}
    for root, _, files in os.walk(doc_dir):
        for file in files:
            if file.endswith(".md"):
                with open(os.path.join(root, file), "r") as md_file:
                    for line in md_file:
                        if line.startswith("# "):
                            index[file] = line[2:].strip()
                            break
    with open(output_path, "w") as file:
        json.dump(index, file, indent=2)

def extract_sender_email(input_path, output_path):
    with open(input_path, "r") as file:
        email_content = file.read()
    email_address = call_llm(f"Extract the sender's email address from this message: {email_content}")
    with open(output_path, "w") as file:
        file.write(email_address)

def extract_credit_card_number(image_path, output_path):
    # Assuming the use of OCR
    from PIL import Image
    import pytesseract

    image = Image.open(image_path)
    card_number = call_llm(f"Extract the credit card number: {pytesseract.image_to_string(image)}")
    with open(output_path, "w") as file:
        file.write(card_number.replace(" ", ""))

def find_similar_comments(input_path, output_path):
    with open(input_path, "r") as file:
        comments = file.readlines()
    prompt = f"Find the most similar pair of comments: {comments}"
    similar_pair = call_llm(prompt).split("\n")
    with open(output_path, "w") as file:
        file.writelines(similar_pair)

def calculate_gold_ticket_sales(db_path, output_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(units * price) FROM tickets WHERE type='Gold'")
    total_sales = cursor.fetchone()[0]
    conn.close()
    with open(output_path, "w") as file:
        file.write(str(total_sales))
