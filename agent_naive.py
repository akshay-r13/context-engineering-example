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
import sqlite3
from typing import List
import re

DATA_PATH = Path(__file__).parent / "data"
DB_PATH = DATA_PATH / "ecommerce.db"
POLICY_DOCUMENT_PATH = DATA_PATH / "policy_document.txt"

@tool
def lookup_order(order_id: str) -> dict:
    """Look up order & shipment details from Ecomm Database based on order_id"""
    tool_result = {}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # get order details such as customer name, address etc.
        cur.execute("SELECT * FROM orders where order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["order_details"] = [dict(r) for r in rows]
        # get shipment details for the order
        cur.execute("SELECT * FROM shipments WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["shipment_details"] = [dict(r) for r in rows]
        # get full list of order items
        cur.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["order_items"] = [dict(r) for r in rows]
    return tool_result

@tool
def find_product(query: str):
    """Find Products from Ecomm Database"""
    pass

@tool
def search_policy(query: str) -> List[str]:
    """Search policy document for relevant chunks of information relevant to user query"""
    top_n = 4
    query_words = re.split("[\s\.,]", query)
    document_chunks = []
    with open(POLICY_DOCUMENT_PATH, "r") as f:
        all_content = f.read(-1)
        document_chunks = all_content.split("\n\n") # split based on paragraph
    chunk_scores = []
    for chunk in document_chunks:
        chunk_words = re.split("[\s\.,]", chunk)
        score = len(set(chunk_words).intersection(query_words))
        chunk_scores.append((chunk, score))
    chunk_scores = [chunk for chunk in chunk_scores if chunk[1] != 0] # filter out irrelevant chunks
    top_chunks = list(sorted(chunk_scores, key=lambda x: x[1], reverse=True))[:top_n]
    return "\n-----\n".join([c[0] for c in top_chunks])


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

print(lookup_order.run(tool_input={"order_id": "ORD-51042"}))

print(search_policy.run(tool_input={"query": "refund return exchange policy"}))