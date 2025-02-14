from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
import json
from openai import OpenAI
from dateutil import parser
from datetime import datetime
def call_function(function,args) :
    if function == "run_script" :
        run_script(args["url"],args["email"])
    elif function == "format_markdown" :
        format_markdown(args["file_path"],args["version"])
    elif function == "count_days" :
        count_days(args["input_file"],args["output_file"],args["day"])

def send_to_llm(task) :

    client = OpenAI(
        api_key="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"
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
