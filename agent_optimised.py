"""
agent_optimised.py
______________

A langgraph customer support agent with clear context engineering applied. This means

1. Clear & Structured System Prompt
2. Message trimming by relevance
3. Retrieval optimised for relevance
5. Capped tool outputs
"""

from pathlib import Path
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_core.tools import tool
import sqlite3
from typing import List
import re
from tabulate import tabulate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_PATH = Path(__file__).parent / "data"
DB_PATH = DATA_PATH / "ecommerce.db"
POLICY_DOCUMENT_PATH = DATA_PATH / "policy_document.txt"
INDEX_PATH = DATA_PATH / "policy_index"

embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004", vertexai=True)

if INDEX_PATH.exists():
    vectorstore = FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
else:
    with open(POLICY_DOCUMENT_PATH) as f:
        text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    vectorstore = FAISS.from_texts(chunks, embeddings)
    vectorstore.save_local(str(INDEX_PATH))

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

@tool
def lookup_order(order_id: str) -> dict:
    """Look up order & shipment details from Ecomm Database based on order_id"""
    tool_result = {}
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # get order details such as customer name, address etc.
        cur.execute("SELECT order_id, customer_name, order_status, order_date, shipping_method  FROM orders where order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["order_details"] = [dict(r) for r in rows]
        # get shipment details for the order
        cur.execute("SELECT carrier, tracking_number, status, estimated_delivery, delay_reason FROM shipments WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["shipment_details"] = [dict(r) for r in rows]
        # get full list of order items
        cur.execute("SELECT product_name, quantity, unit_price FROM order_items WHERE order_id=?", (order_id,))
        rows = cur.fetchall()
        tool_result["order_items"] = [dict(r) for r in rows]
    return tool_result

@tool
def find_product(query_term: str) -> List[dict]:
    """Find Products from Ecomm Database based on a query_term. Term must be 1-2 words"""
    query_term = f"%{query_term.lower()}%"
    tool_result = []
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        find_query = """
        SELECT name, description, price, warranty_months, average_rating, color FROM products
        WHERE
        LOWER(description) LIKE ?
        OR 
        LOWER(name) LIKE ?
        OR 
        LOWER (category) LIKE ?
        OR 
        LOWER(tags) LIKE ?;
        """
        cur.execute(find_query, (query_term, query_term, query_term, query_term,))
        rows = cur.fetchall()
        tool_result = [dict(r) for r in rows]
    return tool_result


@tool
def search_policy(query: str) -> str:
    """Search policy document for information relevant to the query."""
    docs = retriever.invoke(query)
    return "\n\n---\n\n".join(d.page_content for d in docs)

tools = [search_policy, find_product, lookup_order]

AGENT_SYSTEM_PROMPT = """
You are a helpful AI assistant.
Answer user questions concisely.
"""

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    thinking_budget= 0,
    vertexai=True
)

agent = create_agent(
    model=model,
    tools = tools,
    system_prompt = AGENT_SYSTEM_PROMPT
)

messages = []

table = []

while True:
    user_input = input("You: ").strip()
    if user_input.lower() == "quit":
        break
    messages.append({"role": "user", "content": user_input})
    response = agent.invoke({"messages": messages})
    messages = response["messages"]
    print(f"\nAssistant: {messages[-1].content}\n")

    usage = messages[-1].usage_metadata

    table.append({
        "Question": user_input[:60] + "...",
        "Answer": messages[-1].content[:80] + "...",
        "Input Tokens": usage["input_tokens"],
        "Output Tokens": usage["output_tokens"],
        "Total Tokens": usage["total_tokens"]
    })

print(tabulate(table, headers="keys", tablefmt="grid"))