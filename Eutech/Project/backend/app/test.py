import os
import google.generativeai as genai
from google.generativeai.protos import FunctionResponse, Part
from google.generativeai import types
from dotenv import load_dotenv
import json
from tools import python_code_interpreter, AVAILABLE_TOOLS

import os 
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure the Gemini API
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])


agent = create_pandas_dataframe_agent(ChatGoogleGenerativeAI, df=[], verbose=True)

# Define the system prompt (This remains the same)
SYSTEM_PROMPT = """
You are an expert data analyst AI. Your task is to answer user questions about Indoor Air Quality (IAQ) data from a set of files.

You have access to a tool called 'python_code_interpreter'. You MUST use this tool to analyze the data.

**Data Schema & Location:**
- The data is located in the `DATA_DIR` directory.
- Each file in `DATA_DIR` represents a different room and is in .ndjson format (newline-delimited JSON).
- IMPORTANT: The column names for the same metric may vary between files. You MUST write robust code to handle these inconsistencies.
    - Temperature might be 'temp', 'Temp', or 'Temperature (°C)'.
    - CO2 might be 'co2', 'CO2', or 'CO2 (ppm)'.
    - Humidity might be 'rh', 'RH', or 'Relative Humidity (%)'.
- Your Python code should iterate through the files, read them into pandas DataFrames, standardize the column names, and then perform the analysis.

**Output Format:**
- When your analysis is complete, your final step inside the python_code_interpreter should be to `print()` the result.
- Format the final output as a JSON string with a specific structure. The structure should be:
  `{"type": "table" | "text", "data": ...}`
- For tabular data, use this structure:
  `{"type": "table", "data": {"headers": ["Header1", "Header2"], "rows": [["val1", "val2"], ["val3", "val4"]]}}`
- For a plain text answer, use this structure:
  `{"type": "text", "data": "Your textual answer here."}`

**Workflow:**
1. Analyze the user's query.
2. Write Python code to perform the necessary analysis using pandas.
3. Call the `python_code_interpreter` tool with your generated code.
4. The tool will execute your code and return the result (the printed output).
5. If the result is the final answer in the correct JSON format, provide it to the user. If you encounter an error, debug your code and try again.
"""

def get_gemini_model():
    """Initializes and returns the Gemini Pro model configured for tool use."""
    
    # CHANGE 2: The entire manual dictionary definition is replaced by this single line.
    # We pass the function object itself in a list. The library handles the schema generation.
    model = genai.GenerativeModel(
        model_name='gemini-2.5-pro', 
        system_instruction=SYSTEM_PROMPT,
        tools= types.Tool(function_declarations=[python_code_interpreter]) 
    )
    return model

# The rest of the file (run_analysis function) remains exactly the same, as it correctly
# uses the AVAILABLE_TOOLS dictionary to execute the function call.

def run_analysis(user_query: str):
    """
    Runs the full analysis process from user query to final response.
    """
    model = get_gemini_model()
    chat = model.start_chat()
    
    response = chat.send_message(user_query)
    
    while True:
        candidate = response.candidates[0]
        # if not (candidate.content.parts and candidate.content.parts[0].function_call):
        #     print ("HJEJAD")
        #     break

        fc = candidate.content.parts[0].function_call
        tool_name = fc.name
        tool_args = {key: value for key, value in fc.args.items()}

        if tool_name in AVAILABLE_TOOLS:
            tool_function = AVAILABLE_TOOLS[tool_name]
            tool_result = tool_function(**tool_args)
            
            # --- MAJOR CHANGE HERE ---
            # We construct a Part object containing a FunctionResponse.
            # This is the correct way to send tool output back to the model.
            response = chat.send_message(
                Part(function_response=FunctionResponse(
                    name=tool_name,
                    response={"output": tool_result}
                )),
            )
        else:
            response = chat.send_message(
                Part(function_response=FunctionResponse(
                    name=tool_name,
                    response={"output": f"Error: Tool '{tool_name}' not found."}
                )),
            )
            break 
    # --- END OF MAJOR CHANGE ---

    try:
        # Build the final text response by joining the .text from each part that has it.
        # This avoids the ValueError if a part is a function_call.
        final_text = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
        
        if not final_text.strip():
            # Handle cases where the model stops without any final text output.
            raise ValueError("Agent did not produce a final text response.")

        final_answer_json = json.loads(final_text)
        return final_answer_json
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        # Catch errors from JSON parsing or if the response was truly empty/malformed.
        error_message = f"Failed to parse the final response from the agent. Error: {e}"
        # Fallback to a text response with the error details.
        return {"type": "text", "data": error_message}

    
if __name__=="__main__":
    print(run_analysis("What was the average co2 levels in all the rooms?"))