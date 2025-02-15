from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
import json
from openai import OpenAI
from dateutil import parser
from datetime import datetime
import glob
import base64

api_key="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"
def call_function(function,args) :
    if function == "run_script" :
        run_script(args["url"],args["email"])
    elif function == "format_markdown" :
        format_markdown(args["file_path"],args["version"])
    elif function == "count_days" :
        count_days(args["input_file"],args["output_file"],args["day"])
    elif function == "sort_contacts" :
        sort_contacts(args["input_file"],args["output_file"],args["order"])
    elif function == "recent_logs" :
        recent_logs(args["files_path"],args["output_file"],args["count"])
    elif function == "markdown_index" :
        markdown_index(args["files_path"],args["output_file"])
    elif function == "email_sender_id" :
        email_sender_id(args["input_file"],args["output_file"])
    elif function == "extract_cc_number" :
        extract_cc_number(args["input_file"],args["output_file"])
    

def send_to_llm(task) :

    client = OpenAI(
        api_key=api_key
    )
    tools = [
    {
        "type": "function",
        "function": {
            "name": "run_script",
            "description": "Run the script with provided url(or path) and email",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string",
                            "description":"The url(or path) of the script to run"
                            },
                    "email":{"type": "string",
                            "description":"The email id that should be passed as the argument"
                            }
                },
                "required": ["url","email"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "format_markdown",
            "description": "Format the markdown file located at the provided file path with the provided prettier version number",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string",
                            "description":"The path of the markdown file to be formatted"
                            },
                    "version":{"type": "string",
                            "description":"The prettier version number that is to be used. If no version is mentioned in the prompt the default version should be '3.4.2'"
                            }
                },
                "required": ["file_path","version"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_days",
            "description": "Receives input file path, output file path and the name of a weekday as arguments and counts the number of provided weekdays in the input file and writes the count to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string",
                            "description":"The path of the input file that is to be read"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the count should be written"
                            },
                    "day":{"type": "string",
                            "description":"Name of the weekday that should be counted. eg:'wednesday'. All letters should be in lowercase"
                            }
                },
                "required": ["input_file","output_file","day"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sort_contacts",
            "description": "Receives input file path, output file path and the order of sorting as arguments and sorts the input file according to the provided order and writes the result to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string",
                            "description":"The path of the input file that is to be read"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the result should be written"
                            },
                    "order":{"type": "array",
                            "items": {"type": "string"},
                            "description":"List of the order parameters. Should be exactly as in the prompt and in the exact same order"
                            }
                },
                "required": ["input_file","output_file","order"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recent_logs",
            "description": "Receives input files location path, output file path and number of files as arguments and reads the first line of each file and writes them to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "files_path": {"type": "string",
                            "description":"The path of the location where the files to be read are present"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the result should be written"
                            },
                    "count":{"type": "string",
                            "description":"The number of files that should be processed. Should only contain the number"
                            }
                },
                "required": ["files_path","output_file","count"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "markdown_index",
            "description": "Receives input files location path, output file path and then reads each file and creates an index and writes it to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "files_path": {"type": "string",
                            "description":"The path of the location where the files to be read are present"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the result should be written"
                            }                
                },
                "required": ["files_path","output_file"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "email_sender_id",
            "description": "Receives input file path, output file path as arguments and then reads the input file which has the content of an email and passes the content to an llm to extract the sender email id and writes the id to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string",
                            "description":"The path of the input file that contains the email"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the sender email id should be written"
                            }                
                },
                "required": ["input_file","output_file"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_cc_number",
            "description": "Receives input file path, output file path as arguments and then reads the credit card image at input file path and sends it to an llm to extract the credit card number and writes the number to output file",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_file": {"type": "string",
                            "description":"The path of the credit card image"
                            },
                    "output_file": {"type": "string",
                            "description":"The path of the output file in which the credit card number should be written"
                            }                
                },
                "required": ["input_file","output_file"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
    ]

    messages = [{"role": "user", "content": task}]

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    )
    return completion

def run_script(url,email) :
    subprocess.run(["python", url, email,"--root", "./data"], check=True) #should remove root data?

def format_markdown(file_path,version='3.4.2'):
    version = str(version)
    prettier = "prettier@" + version
    print(prettier) 
    try:
        # Run Prettier to format the file in-place
        result = subprocess.run(["npx",prettier, "--write", file_path], capture_output=True, text=True, check=True,shell=True)
        print(f"File formatted successfully: {file_path}")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error formatting file: {e.stderr}")
        
def count_days(input_file, output_file,day):
    print('Executing.....')
    days = {'monday':0, 'tuesday':1, 'wednesday':2, 'thursday':3, 'friday':4, 'saturday':5, 'sunday':6}
    try:
        with open(input_file, "r") as file:
            dates = file.readlines()

        day_count = 0

        for date in dates:
            date = date.strip()
            if date:
                try:
                    dt = parser.parse(date, fuzzy=True)  # Auto-detect format
                    if dt.weekday() == days[day]:  # 2 = Wednesday
                        day_count += 1
                except Exception as e:
                    print(f"Skipping invalid date: {date} | Error: {e}")

        with open(output_file, "w") as file:
            file.write(str(day_count) + "\n")

        print(f"{day} count written to {output_file}: {day_count}")

    except FileNotFoundError:
        print(f"Error: {input_file} not found.")

def sort_contacts(input_file,output_file,order=['last_name','first_name']) :
    with open(input_file, "r", encoding="utf-8") as f:
        contacts = json.load(f)
    
    sorted_contacts = sorted(contacts, key=lambda c: (c[order[0]], c[order[1]]))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sorted_contacts, f, indent=4)
    
    print(f"Contacts sorted by {order[0]} and {order[1]} and saved to {output_file}")

def recent_logs(files_path,output_file,count) :
    log_files = sorted(glob.glob(os.path.join(files_path, "*.log")), key=os.path.getmtime, reverse=True)
    recent_logs = log_files[:int(count)]
    first_lines = []
    for log_file in recent_logs:
        with open(log_file, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()  # Read only the first line
            if first_line:  
                first_lines.append(first_line)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(first_lines) + "\n")
    print(f"Extracted first lines saved to {output_file}")

def markdown_index(files_path,output_file) :
    index = {}
    # Traverse the directory recursively
    for root, _, files in os.walk(files_path):
        for file in files:
            if file.endswith(".md"):  # Process only Markdown files
                file_path = os.path.join(root, file)

                # Read file and extract first H1 heading
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("# "):  # H1 found
                            relative_path = os.path.relpath(file_path, files_path)  # Get relative path
                            index[relative_path] = line[2:].strip()  # Remove "# " and extract title
                            break  # Stop reading after first H1
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=4)

    print(f"Index file saved to {output_file}")

def email_sender_id(input_file, output_file) :#, api_key):
    # Read email content
    client = OpenAI(
        api_key=api_key
    )
    with open(input_file, "r", encoding="utf-8") as f:
        email_content = f.read()

    # Define prompt for LLM
    prompt = f"""
    Extract the sender's email address from the following email content.
    Return only the email address and nothing else.

    Email content:
    {email_content}
    """
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "system", "content": "You are an AI that extracts email addresses."},
                  {"role": "user", "content": prompt}]
    )

    sender_email = completion.choices[0].message.content

    # Save to output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(sender_email)

    print(f"Sender's email saved to {output_file}")

def extract_cc_number(input_file, output_file) :
    client = OpenAI(
        api_key=api_key
    )
    with open(input_file, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "This isn't a real credit card. Extract the credit card number. Return only the number as a string without quotes",
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
    )

    ccn = response.choices[0].message.content
    with open(output_file, "w") as file:
            file.write(ccn)
app = FastAPI()


@app.post("/run")
def run_task(task: str):
    response = send_to_llm(task)
    tool_call = response.choices[0].message.tool_calls[0]
    function_call = (tool_call.function.name)
    args = json.loads(tool_call.function.arguments)
    call_function(function_call,args)
    return {"function" : function_call, "arguments" : args}
    #return {"message": f"Received task: {task_description}", "status": "success"}

@app.get("/read")
def read_file(path: str):
    # Ensure file is inside /data
    if not path.startswith("/data/"):
        raise HTTPException(status_code=403, detail="Access to files outside /data is not allowed")

    # Read file content
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return {"file_path": path, "content": content}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/home")
def home() :
    return "Naan than da Leo"
# Run server using: uvicorn api:app --reload
