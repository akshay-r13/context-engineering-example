"""
agent_naive.py
______________

A langgraph customer support agent with no context engineering principles applied. This means

1. Vague System Prompt
2. No clear message trimming strategy
3. No clear retreival strategy
4. Prompt not formatted clearly
5. No capping of tool outputs
"""

from pathlib import Path

DATA_PATH = Path(__file__).parent / "data"
DB_PATH = DATA_PATH / "ecommerce.db"
POLICY_DOCUMENT_PATH = DATA_PATH / "policy_document.txt"

