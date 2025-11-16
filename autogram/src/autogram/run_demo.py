#!/usr/bin/env python3
"""Simple demo runner: collect -> summarize -> format -> write report.md

This script adjusts sys.path so it can be run from the project root without needing
PYTHONPATH set externally. It expects the environment keys to be available via
`autogram/.env` (autogram package loads it) or the shell.
"""
from __future__ import annotations
import sys
from pathlib import Path

root = Path(__file__).resolve().parent
# Ensure autogram/src is importable without requiring PYTHONPATH externally
sys.path.insert(0, str(root / 'autogram' / 'src'))

from autogram.tools.collector_tool import CollectorTool
from autogram.tools.summarizer_tool import SummarizerTool
from autogram.tools.formatter_tool import FormatterTool
from autogram.tools.veo_tool import VeoTool


def main() -> None:
    query = "recent advances in neuroscience"
    collector = CollectorTool()
    summarizer = SummarizerTool()
    formatter = FormatterTool()

    print("[demo] Collecting web content for query:", query)
    collected = collector._run(query=query, num_results=3)
    if isinstance(collected, str) and collected.startswith("ERROR"):
        print("[demo] Collector error:", collected)
        return

    print("[demo] Collected length:", len(collected))

    # Create a single neuroscience fact sentence
    print("[demo] Creating single neuroscience fact...")
    fact_prompt = (
        "Write ONE clean sentence about the most important neuroscience discovery from this research. "
        "Include the institution name and what they discovered. "
        "Use NO emojis, NO hashtags, NO special characters. Just plain text.\n\n"
        + collected
    )

    script = summarizer._run(text=fact_prompt, max_tokens=50)
    if isinstance(script, str) and script.startswith("ERROR"):
        print("[demo] Summarizer error (script):", script)
        return

    # Format the single fact
    print("[demo] Formatting fact for report")
    formatted_script = formatter._run(text=script, style='markdown')

    # Tool trace (which env vars we saw)
    import os
    from datetime import datetime

    trace_lines = [
        f"Generated: {datetime.utcnow().isoformat()} UTC",
        f"SERPER_KEY present: {bool(os.environ.get('SERPER_KEY'))}",
        f"SERPER_API_KEY present: {bool(os.environ.get('SERPER_API_KEY'))}",
        f"OPENAI_API_KEY present: {bool(os.environ.get('OPENAI_API_KEY'))}",
        f"VEO_KEY present: {bool(os.environ.get('VEO_KEY') or os.environ.get('VEO_API_KEY'))}",
    ]

    out_path = root / 'report.md'
    with out_path.open('w', encoding='utf-8') as f:
        f.write('# Neuroscience Fact\n\n')
        f.write(formatted_script + '\n')

    # Optionally run video generation if RUN_VEO=true in the env
    # By default, run video generation. Set RUN_VEO=false in the env to disable.
    run_veo = os.environ.get('RUN_VEO', 'true').lower() in ('1', 'true', 'yes')
    veo_out = None
    if run_veo:
        print('[demo] RUN_VEO=true — instantiating VeoTool and generating video')
        veo_key = os.environ.get('VEO_KEY') or os.environ.get('VEO_API_KEY')
        if not veo_key:
            print('[demo] VEO key not found in environment; skipping video generation')
        else:
            try:
                veo = VeoTool(api_key=veo_key)
                # Create a direct video generation prompt with the specific fact
                video_prompt = f"A wizard goat character speaking directly to camera saying: '{script.strip()}'. The goat should be clearly visible and speaking the words audibly."

                print(f"[demo] Using report.md as video prompt (chars={len(video_prompt)})")
                veo_out = veo._run(prompt=video_prompt, output_file=str(root / 'autogram_output.mp4'))
                print('[demo] Video generation completed:', veo_out)
            except Exception as e:
                print('[demo] Video generation error:', e)

        # append video info to the report
        with out_path.open('a', encoding='utf-8') as f:
            f.write('\n---\n\n')
            f.write('## Video generation\n\n')
            if veo_out:
                f.write(f'Video file: {veo_out}\n')
            else:
                f.write('Video generation was not run or failed.\n')

    print(f"[demo] Report written to: {out_path}")


if __name__ == '__main__':
    main()
