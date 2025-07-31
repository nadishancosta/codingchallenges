# @title Import necessary libraries
import os

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
from tools import _load_and_prepare_data
from cus_prompt import return_instructions

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
    description="Provides processed data for questions regarding air quality.",
    instruction=return_instructions(),
    tools=[_load_and_prepare_data],
    #     optimize_data_file=True,
    #     stateful=True,
    # )
)

print(f"Agent '{data_analyst_agent.name}' created using model '{AGENT_MODEL}'.")

# @title Setup Session Service and Runner

# --- Session Management ---
# Key Concept: SessionService stores conversation history & state.
# InMemorySessionService is simple, non-persistent storage for this tutorial.
session_service = InMemorySessionService()

# Define constants for identifying the interaction context
APP_NAME = "data_analyst_app"
USER_ID = "user_1"
SESSION_ID = "session_001"  # Using a fixed ID for simplicity

# Create the specific session where the conversation will happen
# session = await
session_service.create_session(
    app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- Runner ---
# Key Concept: Runner orchestrates the agent execution loop.
runner = Runner(
    agent=data_analyst_agent,  # The agent we want to run
    app_name=APP_NAME,  # Associates runs with our app
    session_service=session_service,  # Uses our session manager
)
print(f"Runner created for agent '{runner.agent.name}'.")


# @title Define Agent Interaction Function

from google.genai import types  # For creating message Content/Parts


async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role="user", parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # Default

    # Key Concept: run_async executes the agent logic and yields Events.
    # We iterate through events to find the final answer.
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=content
    ):
        # You can uncomment the line below to see *all* events during execution
        # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        # Key Concept: is_final_response() marks the concluding message for the turn.
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif (
                event.actions and event.actions.escalate
            ):  # Handle potential errors/escalations
                final_response_text = (
                    f"Agent escalated: {event.error_message or 'No specific message.'}"
                )
            # Add more checks here if needed (e.g., specific error codes)
            break  # Stop processing events once the final response is found

    print(f"<<< Agent Response: {final_response_text}")
# We need an async function to await our interaction helper
def run_conversation():
    call_agent_async("What is the average temperature of room 1?",
                                       runner=runner,
                                       user_id=USER_ID,
                                       session_id=SESSION_ID)

if __name__ == "__main__":
    run_conversation()

# --- OR ---

# Uncomment the following lines if running as a standard Python script (.py file):
# import asyncio
# if __name__ == "__main__":
#     try:
#         asyncio.run(run_conversation())
#     except Exception as e:
#         print(f"An error occurred: {e}")