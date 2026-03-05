"""
Mermaid diagram generation powered by deepagents framework.

Uses the local mermaid-skill (SKILL.md + 30 reference docs) to give the agent
full knowledge of Mermaid syntax for all 23+ diagram types.
"""

import re
import logging
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from deepagents import create_deep_agent
from deepagents.backends.utils import create_file_data
from langgraph.checkpoint.memory import MemorySaver

from app.core.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Structured output schema
# ---------------------------------------------------------------------------

class MermaidResponse(BaseModel):
    """Structured response containing generated Mermaid diagram code."""
    mermaid_syntax: str = Field(
        description="Raw Mermaid diagram code (without ```mermaid fences)"
    )


# ---------------------------------------------------------------------------
# Load skill files from local disk into virtual filesystem format
# ---------------------------------------------------------------------------

SKILL_DIR = Path(__file__).parent / "mermaid-skill"


def _load_skill_files() -> dict:
    """Read the mermaid skill directory and return a dict of virtual-path -> file data."""
    files: dict = {}

    # SKILL.md
    skill_md = SKILL_DIR / "SKILL.md"
    if skill_md.exists():
        files["/mermaid-skill/SKILL.md"] = create_file_data(
            skill_md.read_text(encoding="utf-8")
        )

    # All reference docs
    refs_dir = SKILL_DIR / "references"
    if refs_dir.is_dir():
        for ref_file in refs_dir.iterdir():
            if ref_file.is_file() and ref_file.suffix == ".md":
                files[f"/mermaid-skill/references/{ref_file.name}"] = create_file_data(
                    ref_file.read_text(encoding="utf-8")
                )

    logger.info("Loaded %d mermaid skill files into virtual filesystem", len(files))
    return files


# Load once at module import
_skill_files = _load_skill_files()

# ---------------------------------------------------------------------------
# Agent setup
# ---------------------------------------------------------------------------

_checkpointer = MemorySaver()
_SYSTEM_PROMPT = """\
You are an expert Mermaid diagram generator. You have access to a comprehensive \
mermaid skill with documentation for every diagram type.

When the user asks for a diagram:
1. Read the /mermaid-skill/SKILL.md to understand the available diagram types
2. Read the specific reference doc for the chosen diagram type
3. Generate correct, renderable Mermaid code

Rules:
- Return ONLY raw Mermaid code — no markdown fences, no explanations
- Start with the correct diagram type keyword (flowchart, sequenceDiagram, classDiagram, etc.)
- Use clear, semantic node names and labels
- Ensure the syntax is valid and will render correctly
"""

_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
)

_agent = create_deep_agent(
    model=_gemini_model,
    skills=["/mermaid-skill/"],
    response_format=MermaidResponse,
    system_prompt=_SYSTEM_PROMPT,
    checkpointer=_checkpointer,
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _strip_mermaid_fences(text: str) -> str:
    """Remove ```mermaid ... ``` fences if present."""
    text = text.strip()
    text = re.sub(r"^```mermaid\s*\n?", "", text)
    text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def generate_mermaid_with_agent(prompt: str) -> str:
    """Generate Mermaid diagram code using the deepagents framework.

    Args:
        prompt: User description of the desired diagram.

    Returns:
        Raw Mermaid syntax string.

    Raises:
        RuntimeError: If the agent fails to produce a valid response.
    """
    thread_id = uuid4().hex

    result = _agent.invoke(
        {
            "messages": [{"role": "user", "content": prompt}],
            "files": _skill_files,
        },
        config={"configurable": {"thread_id": thread_id}},
    )

    # Extract from structured response
    structured = result.get("structured_response")
    if structured and hasattr(structured, "mermaid_syntax"):
        return _strip_mermaid_fences(structured.mermaid_syntax)

    # Fallback: try to get from last message content
    messages = result.get("messages", [])
    if messages:
        last_content = messages[-1].content if hasattr(messages[-1], "content") else str(messages[-1])
        return _strip_mermaid_fences(last_content)

    raise RuntimeError("DeepAgent did not produce a mermaid diagram response")
