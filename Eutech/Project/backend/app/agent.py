# @title Import necessary libraries
import os
import json
import asyncio

# Gemini libraries and components
from google.adk.agents import Agent

# from google.adk.models.lite_llm import LiteLlm # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types  # For creating message Content/Parts
from google.adk.code_executors import BuiltInCodeExecutor

from dotenv import load_dotenv


# Custom imports
from .tools import _load_and_prepare_data
from .cus_prompt import return_instructions

import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")

import logging

logging.basicConfig(level=logging.ERROR)


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

# print(os.environ["MODEL_NAME"]) = Model name in env file
# print(os.environ["GOOGLE_API_KEY"]) = api key for google in env file


AGENT_DATAFRAME = _load_and_prepare_data()
AGENT_MODEL = os.environ["MODEL_NAME"]
AGENT_NAME = "data_analyst_agent_v1"
APP_NAME = "data_analyst"
USER_ID = "user1234"
SESSION_ID = "session_code_exec_async"

data_analyst_agent = Agent(
    name=AGENT_NAME,
    model=AGENT_MODEL,
    code_executor=BuiltInCodeExecutor(),
    description="Provides processed data for questions regarding air quality.",
    instruction=return_instructions()
)

print(f"Agent '{data_analyst_agent.name}' created using model '{AGENT_MODEL}'.")




async def call_agent_async(query,runner):
    content = types.Content(role="user", parts=[types.Part(text=query)])
    print(f"\n--- Running Query: {query} ---")
    final_response_text = "No final text response captured."
    try:
        # Use run_async
        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            print(f"Event ID: {event.id}, Author: {event.author}")

            # --- Check for specific parts FIRST ---
            has_specific_part = False
            if event.content and event.content.parts:
                for part in event.content.parts:  # Iterate through all parts
                    if part.executable_code:
                        # Access the actual code string via .code
                        
                        print(
                            f"  Debug: Agent generated code:\n```python\n{part.executable_code.code}\n```"
                        )
                        has_specific_part = True
                    elif part.code_execution_result:
                        # Access outcome and output correctly
                        print(
                            f"  Debug: Code Execution Result: {part.code_execution_result.outcome} - Output:\n{part.code_execution_result.output}"
                        )
                        has_specific_part = True
                    # Also print any text parts found in any event for debugging
                    elif part.text and not part.text.isspace():
                        print(f"  Text: '{part.text.strip()}'")
                        # Do not set has_specific_part=True here, as we want the final response logic below

            # --- Check for final response AFTER specific parts ---
            # Only consider it final if it doesn't have the specific code parts we just handled
            if not has_specific_part and event.is_final_response():
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[0].text
                ):
                    final_response_text = event.content.parts[0].text.strip()
                    print(f"==> Final Agent Response: {final_response_text}")
                else:
                    print("==> Final Agent Response: [No text content in final event]")

    except Exception as e:
        print(f"ERROR during agent run: {e}")
    print("-" * 30)
    
    try:
        
        with open(os.path.join(os.path.dirname(__file__), "generated_script.py"), "w") as file:
            file.write(final_response_text[9:-4])
    except Exception as e:
        print(e)


# Execute the main async function
async def run_prompt(query):
    try:
        # Session and Runner
        
        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
        )
        runner = Runner(agent=data_analyst_agent, app_name=APP_NAME, session_service=session_service)
        
        await call_agent_async(query,runner)
        
        from . import generated_script
        
        df = _load_and_prepare_data()
        
        output_JSON = generated_script.process_iaq_query(df)
        
        final_answer_json = json.dumps(output_JSON)
        print(final_answer_json)
        return final_answer_json
    
    except Exception as e:
        # Handle specific error when running asyncio.run in an already running loop (like Jupyter/Colab)
        if "cannot be called from a running event loop" in str(e):
            print("\nRunning in an existing event loop (like Colab/Jupyter).")
            print("Please run `await main()` in a notebook cell instead.")
            # If in an interactive environment like a notebook, you might need to run:
            # await main()
        else:
            raise e  # Re-raise other runtime errors
        
        return await e
