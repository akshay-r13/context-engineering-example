"""
compare_retrieval.py
────────────────────
Run the same query through naive and optimised search_policy tools
and compare the outputs side by side.

Usage:
    uv run python scripts/compare_retrieval.py
"""

import re
import sys
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

DATA_PATH = Path(__file__).parent.parent / "data"
POLICY_DOCUMENT_PATH = DATA_PATH / "policy_document.txt"
INDEX_PATH = DATA_PATH / "policy_index"


# ── Naive: section-based keyword retrieval ────────────────────────────────────

def naive_search_policy(query: str, top_n: int = 3) -> str:
    query_words = set(re.split(r"[\s\.,]", query.lower()))
    with open(POLICY_DOCUMENT_PATH) as f:
        text = f.read()
    sections = re.split(r'(?=SECTION \d+:)', text)
    sections = [s.strip() for s in sections if s.strip()]
    scored = []
    for section in sections:
        section_words = set(re.split(r"[\s\.,]", section.lower()))
        score = len(section_words & query_words)
        if score > 0:
            scored.append((section, score))
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:top_n]
    return "\n-----\n".join(s for s, _ in top)


# ── Optimised: FAISS embedding retrieval ─────────────────────────────────────

embeddings = GoogleGenerativeAIEmbeddings(model="text-embedding-004", vertexai=True)
vectorstore = FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

def optimised_search_policy(query: str) -> str:
    docs = retriever.invoke(query)
    return "\n\n---\n\n".join(d.page_content for d in docs)


# ── Compare ───────────────────────────────────────────────────────────────────

def compare(query: str):
    naive_result = naive_search_policy(query)
    optimised_result = optimised_search_policy(query)

    divider = "=" * 80

    print(f"\n{divider}")
    print(f"QUERY: {query}")
    print(divider)

    print(f"\n{'─'*35} NAIVE {'─'*35}")
    print(f"Characters: {len(naive_result)} | ~Tokens: {len(naive_result)//4}")
    print(f"{'─'*78}\n")
    print(naive_result)

    print(f"\n{'─'*32} OPTIMISED {'─'*32}")
    print(f"Characters: {len(optimised_result)} | ~Tokens: {len(optimised_result)//4}")
    print(f"{'─'*78}\n")
    print(optimised_result)

    print(f"\n{divider}")
    reduction = (1 - len(optimised_result) / len(naive_result)) * 100
    print(f"Size reduction: {reduction:.1f}%")
    print(divider)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = input("Enter query: ").strip()
    compare(query)
