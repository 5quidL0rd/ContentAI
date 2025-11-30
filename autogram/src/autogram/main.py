#!/usr/bin/env python
import sys
import warnings
from datetime import datetime
import os
import sys

from autogram.crew import Autogram
from autogram.instagram_utils import post_to_instagram

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from dotenv import load_dotenv
load_dotenv()

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    inputs = {
        'current_year': str(datetime.now().year)
    }

    try:
        result = Autogram().crew().kickoff(inputs=inputs)

        print("\n=== RAW CREW OUTPUT OBJECT ===")
        print(result)
        print("OUTPUT TYPE:", type(result))
        print("==============================\n")

        # ✓ Correct extraction of text from CrewOutput
        if hasattr(result, "final_output"):
            output_text = result.final_output
        elif hasattr(result, "raw_output"):
            output_text = result.raw_output
        elif hasattr(result, "output"):
            output_text = result.output
        else:
            output_text = str(result)

        print("\n=== EXTRACTED OUTPUT TEXT ===")
        print(output_text)
        print("==============================\n")

        # Detect MP4 filename
        import re
        match = re.search(r'([\w\-_]+\.mp4)', output_text)

        if match:
            video_filename = match.group(1)

            base_dir = r"C:\Users\jayrk\Dev\GatorAI\ContentAI\autogram\src"
            video_path = os.path.join(base_dir, video_filename)

            caption = "Neuroscience Facts"
            print(f"🎬 Detected video: {video_path}")

            post_to_instagram(video_path, caption)
            return

        print("⚠️ No video was posted — MP4 not found in CrewOutput.")

    except Exception as e:
        raise Exception(f"Error while running crew: {e}")


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