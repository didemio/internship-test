\## Part 2 — Code Review



\*\*Problem 1: Hardcoded API Key\*\*

\- What's wrong: API\_KEY = "sk-prod-abc123xyz" is written directly in the code.

\- Why it matters: Anyone who sees the code (e.g. on GitHub) can steal the key and use it, causing unexpected costs or data leaks.

\- Fix: Use environment variables instead: API\_KEY = os.environ\["LLM\_API\_KEY"]



\*\*Problem 2: SQL Injection (two places)\*\*

\- What's wrong: User input is directly concatenated into SQL strings in both search\_documents and save\_answer functions.

\- Why it matters: A user can type: '; DROP TABLE documents; -- and destroy the entire database.

\- Fix: Use parameterized queries:

&#x20; cursor.execute("SELECT ... WHERE content LIKE ?", (f"%{question}%",))

&#x20; conn.execute("INSERT INTO answers VALUES (?, ?)", (question, answer))



\*\*Problem 3: LLM called twice\*\*

\- What's wrong: ask\_llm(q, docs) is called once for print() and again for save\_answer().

\- Why it matters: Doubles the API cost, and the two calls may return different answers — so what gets printed and what gets saved can be different.

\- Fix: Call it once and store the result:

&#x20; answer = ask\_llm(q, docs)

&#x20; print(answer)

&#x20; save\_answer(q, answer)



\*\*Problem 4: No error handling on LLM response\*\*

\- What's wrong: response.json()\["response"] is accessed directly with no checks.

\- Why it matters: If the API returns an error or unexpected format, the whole program crashes.

\- Fix: Wrap in try/except and check response.status\_code before accessing the result.



\## Part 3 — Written Questions



\*\*Q1: SQLite LIKE on 1M rows in Postgres\*\*

The problem is that LIKE '%...%' with a wildcard at the start cannot use a normal index —

Postgres has to scan every single row one by one. On 1M rows this gets very slow.

Fix: Enable pg\_trgm extension and create a GIN index on the content column.

This makes LIKE '%term%' fast. Alternatively use Postgres full-text search (tsvector/tsquery).



\*\*Q2: Sending all documents into the prompt\*\*

If there are thousands of documents, concatenating all of them exceeds the LLM's context

window limit, makes responses slower and more expensive, and confuses the model with

irrelevant content.

Basic RAG fix:

1\. Chunking: split documents into small overlapping pieces (300-500 tokens each)

2\. Embeddings: convert each chunk into a vector and store in a vector database

3\. Top-k retrieval: embed the question, find the 3-5 most similar chunks

4\. Send only those chunks to the LLM — context stays small and relevant



\*\*Q3: LLM API error handling\*\*

1\. Rate limit (429): Too many requests. Fix: retry with exponential backoff (wait 1s, then 2s, then 4s...)

2\. Timeout: API is slow or unreachable. Fix: set a timeout on the request, catch the error, return a fallback message to the user

3\. Unexpected response: API returned an error object without the expected "response" key. Fix: wrap in try/except KeyError, log the raw response, return a safe default instead of crashing



\*\*Q4 (Bonus): Postgres schema for chatbot with user history\*\*

Two tables:



CREATE TABLE conversations (

&#x20;   id         SERIAL PRIMARY KEY,

&#x20;   user\_id    TEXT NOT NULL,

&#x20;   created\_at TIMESTAMPTZ DEFAULT NOW()

);



CREATE TABLE messages (

&#x20;   id              SERIAL PRIMARY KEY,

&#x20;   conversation\_id INTEGER REFERENCES conversations(id),

&#x20;   role            TEXT NOT NULL,  -- 'user' or 'assistant'

&#x20;   content         TEXT NOT NULL,

&#x20;   created\_at      TIMESTAMPTZ DEFAULT NOW()

);



At query time: fetch the last N messages for the conversation and include them in the prompt as history.


## Time Spent
Approximately 1 hour.
