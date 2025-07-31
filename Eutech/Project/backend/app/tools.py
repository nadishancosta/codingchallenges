import os
import io
import pandas as pd
from contextlib import redirect_stdout

# Define the path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

def python_code_interpreter(code: str) -> str:
    """
    Executes a string of Python code and returns the output.
    The code has access to the pandas library (pd) and the DATA_DIR variable.
    The final result should be printed as a JSON string to stdout.
    Example of a valid print statement for a final answer:
    print(df.to_json(orient='split'))
    """
    try:
        # Create a dictionary to serve as the local namespace for exec
        local_vars = {
            'pd': pd,
            'os': os,
            'DATA_DIR': DATA_DIR,
            '__builtins__': __builtins__ # Ensure basic builtins are available
        }
        
        # Use StringIO to capture the output of print statements
        f = io.StringIO()
        with redirect_stdout(f):
            exec(code, {"pd": pd, "os": os, "DATA_DIR": DATA_DIR}, local_vars)
        
        output = f.getvalue()
        
        # If there's no print output, we try to get the last evaluated expression
        # This is a bit more advanced but can be useful. For now, we rely on print.
        if not output and local_vars.get('result'):
             output = str(local_vars.get('result'))

        if not output:
            return "Code executed successfully, but produced no output. Remember to use the 'print()' function to output your final result as a string, preferably in JSON format."
        
        return output

    except Exception as e:
        return f"Error executing code: {str(e)}"

# This is a dictionary that maps tool names to their functions.
# The agent will use these names to call the tools.
AVAILABLE_TOOLS = {
    "python_code_interpreter": python_code_interpreter,
}