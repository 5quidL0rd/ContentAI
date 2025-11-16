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

    # 1) Research summary (structured, cite sources)
    print("[demo] Creating structured research summary...")
    research_prompt = (
        "You are an expert neuroscience researcher. Read the collected web snippets below and produce:\n"
        "1) A concise research summary (3-6 bullet findings) with citations in parentheses when sources are present;\n"
    "2) A short 'elevator pitch' (1-2 sentences) suitable as a social media hook;\n"
        "3) A list of the original sources (URLs) identified in the collected text.\n\n"
        "Collected content:\n\n"
        + collected
    )

    research = summarizer._run(text=research_prompt, max_tokens=600)
    if isinstance(research, str) and research.startswith("ERROR"):
        print("[demo] Summarizer error (research):", research)
        return

    # 2) Create a full educational video script (wizard goat persona) from the research
    print("[demo] Creating full educational video script (wizard goat)...")
    script_prompt = (
        "You are creating a detailed educational video script for the 'Wizard Goat' - a wise, magical goat character who explains science in an engaging way.\n\n"
        "Write a FULL video script (2-3 minutes) with:\n"
        "- Wizard Goat introduction: 'Greetings, mortals! I am the Wizard Goat, your guide to the mysteries of science!'\n"
        "- Detailed narration explaining each research finding in the Wizard Goat's voice\n"
        "- Use phrases like 'Behold!', 'Witness the power of science!', 'My magical knowledge reveals...'\n"
        "- Include specific dialogue for each key finding\n"
        "- End with: 'Remember, young scholars, science is the greatest magic of all! Until next time, this is your Wizard Goat, signing off!'\n"
        "- Make it conversational and engaging, as if the Wizard Goat is actually speaking to the audience\n\n"
        "Research to explain:\n\n"
        + research
    )

    script = summarizer._run(text=script_prompt, max_tokens=1200)
    if isinstance(script, str) and script.startswith("ERROR"):
        print("[demo] Summarizer error (script):", script)
        return

    # Format both outputs
    print("[demo] Formatting outputs for report")
    formatted_research = formatter._run(text=research, style='markdown')
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
        f.write('# Autogram Demo Report\n\n')
        f.write(f'**Query:** {query}\n\n')
        f.write('---\n\n')
        f.write('## Research Summary\n\n')
        f.write(formatted_research + '\n\n')
        f.write('---\n\n')
        f.write('## Educational Video Script (Wizard Goat)\n\n')
        f.write(formatted_script + '\n\n')
        f.write('---\n\n')
        f.write('## Tool trace\n\n')
        for line in trace_lines:
            f.write(f'- {line}\n')

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
                # Use the generated report.md as the prompt for the video tool.
                # Read the report and trim to a reasonable length if necessary.
                try:
                    report_text = (root / 'report.md').read_text(encoding='utf-8')
                except Exception:
                    report_text = script

                # Trim to first 30k characters to avoid excessively large prompts
                max_prompt_len = 30000
                video_prompt = report_text[:max_prompt_len]

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
