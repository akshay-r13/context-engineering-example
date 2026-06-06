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
from langchain.agents import create_agent
from langchain_core.tools import tool

DATA_PATH = Path(__file__).parent / "data"
DB_PATH = DATA_PATH / "ecommerce.db"
POLICY_DOCUMENT_PATH = DATA_PATH / "policy_document.txt"

@tool
def lookup_order(order_id: str):
    """Look up order from Ecomm Database based on ID"""
    pass

@tool
def find_product(query: str):
    """Find Products from Ecomm Database"""
    pass

@tool
def read_policy(query: str):
    """Read policy document"""
    pass


AGENT_SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer user questions concisely.
"""

agent = create_agent(
    model="gemini-2.5-flash",
    tools = [],
    system_prompt = AGENT_SYSTEM_PROMPT
)

response = agent.invoke({
    "messages": [
        "Hey can you help me?"
    ]
})

print(response)