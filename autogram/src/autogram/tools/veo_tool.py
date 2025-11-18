# autogram/tools/veo_tool.py
import time
from typing import Any, Optional

from crewai.tools.base_tool import BaseTool
from google import genai
from google.genai import types

import os


class VeoTool(BaseTool):
    """Generates videos using Google Veo 3 as a CrewAI tool."""

    name: str = "veo_tool"
    description: str = "Generates a video using Google Veo 3 based on a text prompt or a script file."

    # Runtime fields
    api_key: Optional[str] = None
    client: Optional[Any] = None

    def __init__(self, api_key: Optional[str] = None):
        # Initialize BaseTool (pydantic) default behavior
        super().__init__()

        # Resolve api key from argument or environment
        self.api_key = api_key or os.environ.get('VEO_KEY') or os.environ.get('VEO_API_KEY')
        if not self.api_key:
            # Don't raise here; allow instantiation for dry-run and surface errors at runtime
            self.client = None
            return

        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception:
            # If client creation fails, set client to None and allow _run to raise
            self.client = None

    def _run(self, prompt: str | None = None, from_file: str | None = None, output_file: str = "autogram_output.mp4") -> str:
        """l
        CrewAI will call this method internally when the agent uses the tool.

        Provide either `prompt` or `from_file` (path to a text file containing the prompt).
        Returns the path to the generated video file.
        """

        if from_file and not prompt:
            with open(from_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()

        if not prompt:
            raise ValueError("No prompt provided to VeoTool. Please pass a text prompt or file path.")

        print("Generating video from script...")

        operation = self.client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
        )

        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)
            operation = self.client.operations.get(operation)

        generated_video = operation.response.generated_videos[0]
        self.client.files.download(file=generated_video.video)
        generated_video.video.save(output_file)
        print(f"Video saved to {output_file}")

        return output_file
