import google.generativeai as genai
import os
import pandas as pd
import json
from io import StringIO

# --- Configure Gemini API ---
# print(os.environ["GOOGLE_API_KEY"])
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
except KeyError:
    print("ERROR: GOOGLE_API_KEY environment variable not set.")
    exit()

# --- Data Loading (Helper Function) ---

def _load_and_prepare_data():
    """Loads all sensor data into a single, normalized pandas DataFrame."""
    data_dir = './sensor_data'
    if not os.path.exists(data_dir):
        return None
        
    all_data = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.ndjson'):
            room_name = filename.split('.')[0]
            file_path = os.path.join(data_dir, filename)
            try:
                # Read line-delimited JSON
                with open(file_path, 'r') as f:
                    df = pd.read_json(f, lines=True)
                
                # Normalize columns
                column_map = {'temp': 'temperature', 'CO2 (PPM)': 'co2'}
                df.rename(columns=lambda c: column_map.get(c.strip(), c.strip()), inplace=True)
                
                df['room'] = room_name
                all_data.append(df)
            except Exception as e:
                print(f"Error reading or processing {filename}: {e}")
                continue
                
    if not all_data:
        return None

    df = pd.concat(all_data, ignore_index=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# --- Agent's Tool: Code Execution ---

def execute_python_code(code: str):
    """
    Executes a string of Python code and returns the result.
    The code must assign its results to two variables:
    - `text_answer` (string): The natural language answer.
    - `table_data` (list of dicts or None): The tabular data for the frontend.
    
    Args:
        code: A string containing the Python code to execute.
    
    Returns:
        A JSON string with the execution result.
    """
    print("\n--- Executing Generated Code ---\n")
    print(code)
    print("\n------------------------------\n")
    
    try:
        # Prepare the execution environment
        df = _load_and_prepare_data()
        if df is None:
            return json.dumps({"text": "Error: Could not load data for analysis."})

        local_scope = {'df': df, 'pd': pd}
        
        # Execute the code
        # WARNING: Using exec is a security risk. For production, use a sandboxed environment.
        exec(code, globals(), local_scope)
        
        # Retrieve results from the local scope
        text_answer = local_scope.get('text_answer', 'Could not determine a textual answer from the code.')
        table_data = local_scope.get('table_data', None)

        return json.dumps({"text": text_answer, "table": table_data})

    except Exception as e:
        print(f"Error during code execution: {e}")
        return json.dumps({"text": f"An error occurred while executing the analysis code: {e}"})

# --- Main Agent Orchestration ---

def process_query(query: str):
    """Processes the user query using the Gemini model and our code execution tool."""
    
    # Define the tool for the Gemini model
    tools = [genai.protos.Tool(
        function_declarations=[
            genai.protos.FunctionDeclaration(
                name='execute_python_code',
                description="Executes Python code using a pandas DataFrame (`df`) to answer a user's query about air quality data. The code must produce a text answer and optionally a table.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        'code': genai.protos.Schema(type=genai.protos.Type.STRING, description="The Python code to execute.")
                    },
                    required=['code']
                )
            )
        ]
    )]

    # Create the Gemini model instance with the tool
    model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=tools)

    # Create the prompt for the model
    system_prompt = f"""
    You are a data analyst assistant. You have access to a pandas DataFrame named `df`.
    The DataFrame schema is: ['timestamp' (datetime), 'temperature' (float), 'humidity' (float), 'co2' (float), 'room' (string)].

    Your task is to answer the user's query by writing and executing a Python script.

    User Query: "{query}"

    Instructions:
    1. Write a Python script that uses the `df` to perform the necessary analysis.
    2. Your script MUST assign the final textual answer to a variable named `text_answer`.
    3. If the answer requires a data table, create a list of dictionaries and assign it to a variable named `table_data`. The table should be clean and readable. Round floats to 2 decimal places. If no table is needed, set `table_data = None`.
    4. Call the `execute_python_code` function with your complete script as the `code` argument. Do not use markdown backticks.
    """

    try:
        # Send the prompt to the model
        response = model.generate_content(system_prompt)
        
        # Check if the model responded with a tool call
        if response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            if function_call.name == 'execute_python_code':
                # Extract the generated code
                code_to_execute = function_call.args['code']
                
                # Execute the code using our tool
                result_json = execute_python_code(code_to_execute)
                return json.loads(result_json)
        else:
            # If the model didn't use the tool, return its text response
            return {"text": response.text, "table": None}

    except Exception as e:
        print(f"An error occurred while interacting with the Gemini API: {e}")
        return {"text": f"An error occurred: {e}", "table": None}