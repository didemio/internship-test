<img width="1204" height="101" alt="image" src="https://github.com/user-attachments/assets/80fbb999-bf03-4573-8cd2-975738638a67" /># Internship Preliminary Test — Answers

## Time Spent
Approximately 1 hour.

---

## Part 2 — Code Review

**Problem 1: Hardcoded API Key**
- What's wrong: `API_KEY = "sk-prod-abc123xyz"` is written directly in the code.
- Why it matters: Anyone who sees the code publicly can easily steal the key and use it, causing unexpected costs or data leaks.
- Fix: Use environment variables instead: `API_KEY = os.environ["LLM_API_KEY"]`

**Problem 2: SQL Injection (two places)**
- What's wrong: User input is directly merged into SQL strings in both `search_documents` and `save_answer` functions.
- Why it matters: A user can type `'; DROP TABLE documents; --` and destroy the entire database.
- Fix: Use parameterized queries:
```python
cursor.execute("SELECT ... WHERE content LIKE ?", (f"%{question}%",))
conn.execute("INSERT INTO answers VALUES (?, ?)", (question, answer))
```

**Problem 3: LLM called twice**
- What's wrong: `ask_llm(q, docs)` is called once for `print()` and again for `save_answer()`.
- Why it matters: Doubles the API cost, and the two calls may return different answers, so what gets printed and what gets saved can be different.
- Fix: Call it once and store the result:
```python
answer = ask_llm(q, docs)
print(answer)
save_answer(q, answer)
```

**Problem 4: No error handling on LLM response**
- What's wrong: `response.json()["response"]` is accessed directly with no checks.
- Why it matters: If the API returns an error or unexpected format, the whole program crashes.
- Fix: Wrap in try/except and check `response.status_code` before accessing the result.

---

## Part 3 — Written Questions

**Q1: SQLite LIKE on 1M rows in Postgres**

LIKE '%...%' becomes slow first because the % at the beginning prevents Postgres from using a normal index, so it may scan all 1,000,000 rows.

Fix: I would fix it by adding a pg_trgm GIN index for faster partial text search.
For more advanced document searching, I would use Postgres full-text search with tsvector and tsquery.

---

**Q2: Sending all documents into the prompt**

Sending all documents is not a good idea because the prompt can become too large, slow, expensive, and full of irrelevant information that confuses the LLM.

Fix: A basic RAG approach fixes this by splitting documents into smaller chunks, creating embeddings for each chunk, and retrieving only the top-k most relevant chunks for the user’s question.
Then only those selected chunks are sent to the LLM, so the answer is faster, cheaper, and more focused.

---

**Q3: LLM API error handling**

Three common failures are rate limits, timeouts, and unexpected API responses.  
In production, I would handle rate limits with exponential backoff retries, handle timeouts with request limits and fallback messages, and validate the API response before reading fields from it.  
I would also log these errors so they can be monitored and debugged later.
---

**Q4 (Bonus): Postgres schema for chatbot with user history**

```sql
CREATE TABLE conversations (
    id         SERIAL PRIMARY KEY,
    user_id    TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE messages (
    id              SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role            TEXT NOT NULL,  -- 'user' or 'assistant'
    content         TEXT NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
```

At query time: fetch the last N messages for the conversation and include them in the prompt as history.
