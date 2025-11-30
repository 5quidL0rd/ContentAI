# autogram/tools/veo_tool.py

import time
from typing import Any, Optional, Type

from pydantic import BaseModel, Field
from crewai.tools.base_tool import BaseTool
from google import genai

# -------------------------
# FIX: Proper argument schema
# -------------------------
class VeoToolSchema(BaseModel):
    prompt: Optional[str] = Field(
        None, description="Text prompt for generating the video"
    )
    from_file: Optional[str] = Field(
        None, description="Path to a text file containing the script"
    )
    output_file: str = Field(
        "autogram_output.mp4", description="Where to save the resulting video"
    )

    model_config = {"extra": "ignore"}

    # Require at least one of the two
    def model_post_init(self, __context):
        if not self.prompt and not self.from_file:
            raise ValueError("Either `prompt` or `from_file` is required.")


# -------------------------
# TOOL CLASS
# -------------------------
class VeoTool(BaseTool):
    name: str = "veo_tool"
    description: str = "Generates a video using Google Veo 3 based on a text prompt or script file."
    args_schema: Type[BaseModel] = VeoToolSchema

    api_key: Optional[str] = None
    client: Optional[Any] = None

    def __init__(self, api_key: str):
        super().__init__()
        self.api_key = api_key
        self.client = genai.Client(api_key=api_key)

    def _run(self, prompt: str = None, from_file: str = None, output_file: str = "autogram_output.mp4") -> str:

        # Load from script file if needed
        if from_file and not prompt:
            with open(from_file, "r", encoding="utf-8") as f:
                prompt = f.read().strip()

        if not prompt:
            raise ValueError("No prompt provided to VeoTool. Provide prompt or from_file.")

        print("Generating video…")

        operation = self.client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
        )

        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)
            operation = self.client.operations.get(operation)

        generated_video = operation.response.generated_videos[0]
        file_bytes = self.client.files.download(file=generated_video.video)

        with open(output_file, "wb") as f:
            f.write(file_bytes)

        print(f"Video saved to {output_file}")

        return output_file
