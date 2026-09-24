import os

MOCK_LLM = os.getenv("MOCK_LLM", "1")
import chromadb
from pathlib import Path
from sentence_transformers import SentenceTransformer
documents = []
ids = []

for i in range(1, 9):
    with open(f"docs/doc_{i:02d}.txt", "r", encoding="utf-8") as f:
        documents.append(f.read())

    ids.append(f"doc_{i:02d}")

print("Documents:", len(documents))
print("IDs:", ids)


# 2. Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# 3. Generate embeddings
embeddings = model.encode(documents)

print("Embeddings created:", embeddings.shape)


# 4. Create ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="documents"
)


# 5. Store documents + embeddings
collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings.tolist()
)

print("Stored in ChromaDB:", collection.count())


prompt_template = """
ROLE:You are a helpful question-answering assistant.

CONTEXT:Use the following retrieved context to answer the question:{context}

TASK:Answer the user's question using the provided context.

FORMAT:Give a direct answer in plain text. If the context does not contain
enough information, state that the answer cannot be determined from
the provided context.

LENGTH:Keep the answer concise, preferably 2-5 sentences.

NEGATIVE CONSTRAINT:Do not use information that is not present in the provided context.
Do not invent, assume, or add unsupported facts.

FEW-SHOT EXAMPLE:

Context:
Python was created by Guido van Rossum and first released in 1991.

Question:
Who created Python?

Answer:
Python was created by Guido van Rossum.

NOW ANSWER:

Question:{question}"""


from typing import TypedDict

class GraphState(TypedDict):
  query: str
  intent: str
  answer: str
  sources: list[str]
  confidence: float


def classify_intent(state: GraphState):
  query = state["query"].lower()

  keywords = [
      "delivery",
      "return",
      "refund",
      "membership",
      "tracking",
      "cancel",
      "gift card",
      "support hours"
  ]

  if MOCK_LLM != "0":
      if any(keyword in query for keyword in keywords):
          intent = "policy_question"
      else:
          intent = "general_question"

  else:
      # Optional real LLM implementation later
      intent = "general_question"

  return {"intent": intent}

from pydantic import BaseModel, Field

class AnswerOutput(BaseModel):
  answer: str
  sources: list[str]
  confidence: float = Field(ge=0, le=1)

def retrieve_and_answer(state: GraphState):

  query = state["query"]

  results = collection.query(
      query_texts=[query],
      n_results=3
  )

  retrieved_chunks = results["documents"][0]
  retrieved_ids = results["ids"][0]

  if MOCK_LLM != "0":
      top_chunk_snippet = retrieved_chunks[0][:200]

      answer = f"Based on the retrieved context: {top_chunk_snippet}"

      output = AnswerOutput(
          answer=answer,
          sources=retrieved_ids,
          confidence=1.0
      )

      return {
          "answer": output.answer,
          "sources": output.sources,
          "confidence": output.confidence
      }


def direct_answer(state: GraphState):

    if MOCK_LLM != "0":

      output = AnswerOutput(
          answer="I can only answer questions about Zepto policies right now.",
          sources=[],
          confidence=1.0
      )

      return {
          "answer": output.answer,
          "sources": output.sources,
          "confidence": output.confidence
      }

def route_intent(state: GraphState):
    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"



from langgraph.graph import StateGraph, START, END

graph = StateGraph(GraphState)

graph.add_node("classify_intent", classify_intent)
graph.add_node("retrieve_and_answer", retrieve_and_answer)
graph.add_node("direct_answer", direct_answer)



graph.add_edge(START, "classify_intent")

graph.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

graph.add_edge("retrieve_and_answer", END)
graph.add_edge("direct_answer", END)


app_graph = graph.compile()



result = app_graph.invoke({"query": "How can I get a refund?"})
print(result)


from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AskRequest(BaseModel):
  query: str

@app.post("/ask", response_model=AnswerOutput)
def ask(request: AskRequest):
  result = app_graph.invoke({
      "query": request.query
  })

  return AnswerOutput(
      answer=result["answer"],
      sources=result["sources"],
      confidence=result["confidence"]
  )