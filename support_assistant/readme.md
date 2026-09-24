## RAG Pipeline Architecture

The application follows a Retrieval-Augmented Generation (RAG) pipeline consisting of four main stages: **ingestion → embedding → retrieval → generation**.

### 1. Ingestion

The policy documents are stored in the `docs/` directory as `doc_01.txt` through `doc_08.txt`.

The documents are loaded in the application using the document-loading code in `main.py`. Since each document is small, each document is treated as a single chunk. The document text is stored in the `docs` list, while the corresponding document IDs (`doc_01`, `doc_02`, etc.) are stored separately in the `ids` list.

### 2. Embedding

The document chunks are converted into numerical vector embeddings using the local Sentence Transformers model:

`all-MiniLM-L6-v2`

The embeddings are generated using:

```python
model.encode(docs)
```

The resulting vectors have 384 dimensions. No external LLM or embedding API is required.

The embeddings and their corresponding document text and IDs are stored in the ChromaDB collection:

`documents`

ChromaDB is configured to use cosine similarity for vector search.

### 3. Retrieval

When a user sends a question to the `/ask` endpoint, the LangGraph workflow first executes the `classify_intent` node.

If the question contains policy-related keywords such as `refund`, `return`, `delivery`, `tracking`, or `membership`, it is classified as a `policy_question`.

The conditional edge then routes the question to the `retrieve_and_answer` node.

Inside this node, the query is converted into an embedding using the same `all-MiniLM-L6-v2` model. ChromaDB then compares the query embedding against the stored document embeddings using cosine similarity and retrieves the top 3 most similar document chunks.

The retrieved document IDs are also stored as the `sources` field in the final response.

### 4. Generation

For a policy question, the `retrieve_and_answer` node uses the retrieved context to produce the answer.

When `MOCK_LLM` is in its default state (`MOCK_LLM` unset or `MOCK_LLM=1`), no external LLM is called. Instead, the node deterministically generates an answer using the most similar retrieved chunk:

```text
Based on the retrieved context: <top retrieved chunk>
```

For a general question, the `classify_intent` node routes the request to the `direct_answer` node. In mock mode, this node returns the fixed response:

```text
I can only answer questions about Zepto policies right now.
```

The final response is validated using the `AnswerOutput` Pydantic model containing:

* `answer` — generated answer
* `sources` — retrieved document/chunk IDs
* `confidence` — confidence value between 0 and 1

### Pipeline Flow

```text
                User Question
                     │
                     ▼
              FastAPI /ask
                     │
                     ▼
             classify_intent
                │         │
       policy_question   general_question
                │         │
                ▼         ▼
       retrieve_and_   direct_answer
          answer            │
                │            │
                ▼            │
        ChromaDB Retrieval   │
          Top-3 chunks       │
                │            │
                └──────┬─────┘
                       ▼
                 AnswerOutput
             (answer + sources
               + confidence)
                       │
                       ▼
                  JSON Response
```

### `MOCK_LLM` Behavior

The `MOCK_LLM` environment variable controls only the **generation/LLM-dependent parts** of the workflow. Intent routing and document retrieval remain real and are not replaced by mock logic.

By default, when `MOCK_LLM` is unset or set to `1`:

* Intent classification uses the required keyword-based heuristic.
* ChromaDB performs real vector retrieval.
* Policy answers are generated deterministically from the top retrieved chunk.
* General questions receive the fixed canned response.
* No external LLM API call is made.

When `MOCK_LLM=0`, the optional real-LLM path can be used for generation and direct answers. The retrieved context and the structured prompt are then supplied to the LLM, while the final response is still validated against the `AnswerOutput` schema.

Thus, the core RAG pipeline remains:

**Documents → Embeddings → ChromaDB → Retrieval → Answer Generation → Validated JSON**
