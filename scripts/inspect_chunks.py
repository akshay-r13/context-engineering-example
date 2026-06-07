from pathlib import Path
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores import FAISS

DATA_PATH = Path(__file__).parent / "data"
INDEX_PATH = DATA_PATH / "policy_index"

embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
vectorstore = FAISS.load_local(str(INDEX_PATH), embeddings, allow_dangerous_deserialization=True)

docs = vectorstore.docstore._dict
print(f"Total chunks: {len(docs)}\n")

for i, (_, doc) in enumerate(docs.items()):
    print(f"--- Chunk {i+1} ({len(doc.page_content)} chars / ~{len(doc.page_content)//4} tokens) ---")
    print(doc.page_content)
    print()
