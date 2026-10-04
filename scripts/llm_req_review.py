#!/usr/bin/env python3
"""LLM-assisted requirement review — LangChain SKELETON (you complete it).

Task C of Assignment 1: YOU build the AI reviewer. A human checklist catches the
obvious problems; this script must catch the SEMANTIC ones — hidden ambiguity,
untestable claims, non-atomic behaviour, and contradictions BETWEEN requirements.

Setup (once) — free, local, no API key:
    # macOS
    brew install ollama && brew services start ollama
    ollama pull llama3.2
    python3 -m venv .venv
    .venv/bin/pip install langchain langchain-ollama
    # Windows (PowerShell):
    #   winget install Ollama.Ollama
    #   ollama pull llama3.2
    #   py -m venv .venv
    #   .venv\\Scripts\\pip install langchain langchain-ollama

Run:
    .venv/bin/python scripts/llm_req_review.py requirements.csv > review-output.md

What you must do (the graded part):
  1. Complete the PROMPT — prompt engineering: tell the model exactly what counts
     as a defect (ISO/IEC/IEEE 29148: unambiguous, complete, consistent,
     verifiable, singular, feasible, traceable), what to ignore, and the exact
     output format you want back.
  2. Complete the model call where marked TODO (use ChatOllama).
  3. Run it, then JUDGE each finding: accept or reject with a one-line reason.
     Record the confirmed defects, your prompt, and your accept/reject decisions
     in the DEFECT-REVIEW section of your SRS.
  The tool proposes; you decide. Submitting raw LLM output as your review
  receives no credit.
"""
import sys

# ---------------------------------------------------------------------------
# 1. THE PROMPT — complete it. What you write here is the assignment.
# ---------------------------------------------------------------------------
PROMPT = """You are a requirements-quality reviewer for a Software Requirements
Specification (SRS) of a Pac-Man game's core logic.

Review the requirements below for defects. A defect is a violation of one of
the ISO/IEC/IEEE 29148 quality characteristics:

- Unambiguous: flag a requirement if it can reasonably be interpreted in more than
  one way, or if it uses vague or subjective terms such as "fast", "easy",
  "appropriate", "user-friendly", or "should".
- Complete: flag a requirement if necessary conditions, actors, triggers, inputs,
  outputs, or expected system responses are missing.
- Consistent: flag a requirement if it conflicts with or contradicts another
  requirement.
- Verifiable: flag a requirement if there is no concrete test or observation that
  could determine whether the requirement has been satisfied.
- Singular: flag a requirement if it combines multiple independent behaviours or
  obligations that should be separated into individual requirements.
- Feasible: flag a requirement if it describes behaviour that is outside the
  stated system scope or cannot reasonably be implemented by the JPacman core logic.
- Traceable: flag a requirement if it does not identify a concrete implementation
  source such as a class and method that supports the behaviour.

Do not flag purely stylistic preferences, punctuation, capitalization, formatting,
or wording differences that do not affect the meaning, testability, or correctness
of the requirement.

Also compare requirements against each other and flag:
- direct contradictions,
- logically incompatible behaviours,
- duplicate requirements that specify the same behaviour,
- overlapping requirements that could create inconsistent interpretations.

For each defect found, output exactly one line:
  <REQ-ID> | <characteristic violated> | <one-sentence explanation> | <suggested fix>

If a requirement is clean, do not mention it.

Requirements:
{requirements}
"""

def load_requirements(path: str) -> str:
    """Extract requirement lines from an SRS text file or a Requirement Yogi CSV export."""
    if path.lower().endswith(".csv"):
        import csv, re
        reqs = []
        with open(path, newline="", encoding="utf-8-sig") as fh:
            for row in csv.reader(fh):
                key = next((c.strip() for c in row
                            if re.match(r"^[A-Z][A-Z0-9]{1,9}-\d+$", c.strip())), None)
                if key:
                    reqs.append(key + ". " + " ".join(c.strip() for c in row if c.strip() != key))
    else:
        import re as _re
        lines = open(path, encoding="utf-8").read().splitlines()
        reqs = [l for l in lines if _re.match(r"^[A-Z][A-Z0-9]{1,9}-\d+", l.strip().lstrip("-* "))]
    if not reqs:
        sys.exit("No requirement lines (e.g., SJC-001) found in " + path)
    return "\n".join(reqs)

def review(path: str) -> None:
    requirements = load_requirements(path)
    prompt = PROMPT.format(requirements=requirements)

    # -----------------------------------------------------------------------
    # 2. THE MODEL CALL — complete it (LangChain + local Ollama).
    # -----------------------------------------------------------------------
    from langchain_ollama import ChatOllama

    model = ChatOllama(
        model="llama3.2",
        temperature=0
    )

    print(model.invoke(prompt).content)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: llm_req_review.py requirements.csv"); sys.exit(2)
    review(sys.argv[1])
