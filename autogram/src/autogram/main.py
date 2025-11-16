#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
from autogram import get_openai_key
import sys

from autogram.crew import Autogram
from autogram.instagram_utils import post_to_instagram

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew for neuroscience content extraction.
    """
    inputs = {
        'current_year': str(datetime.now().year)
    }
    
    api_key = get_openai_key()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment.\n"
              "Create a .env file (see .env.example) and add your key as OPENAI_API_KEY=YOUR_KEY\n"
              "The crew will likely fail without a valid key.")
        # Continue anyway so users can run non-API parts or see more errors


    try:
        result = Autogram().crew().kickoff(inputs=inputs)

        if isinstance(result, dict):
            video = result.get("video_path")
            caption = result.get("caption")
            if video and caption:
                post_to_instagram(video, caption)

    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Autogram().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Autogram().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Autogram().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
      run()