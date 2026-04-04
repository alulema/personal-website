---
title: Asyncio in Python — A Practical Guide
description: A deep dive into Python's asyncio library, covering coroutines, event loops, tasks, and real-world patterns for building high-performance async applications.
publishDate: 2024-03-15
tags:
  - python
  - asyncio
  - performance
  - backend
lang: en
draft: false
---

## Why Async Matters

Modern applications spend most of their time *waiting* — for databases, external APIs, file I/O. Traditional synchronous code blocks the entire thread during these waits. Asyncio lets you do useful work while waiting.

## Coroutines vs Threads

A coroutine is a function that can pause and resume execution. Unlike threads, coroutines are cooperatively scheduled — they yield control explicitly, which means no race conditions and minimal overhead.

```python
import asyncio

async def fetch_data(url: str) -> dict:
    # Simulates an async HTTP call
    await asyncio.sleep(1)
    return {"url": url, "data": "..."}
```

## Running Coroutines Concurrently

The real power comes from running multiple coroutines at once:

```python
async def main():
    tasks = [
        fetch_data("https://api.example.com/users"),
        fetch_data("https://api.example.com/posts"),
        fetch_data("https://api.example.com/comments"),
    ]
    results = await asyncio.gather(*tasks)
    return results

asyncio.run(main())
```

This runs all three requests concurrently, reducing total wait time from 3s to ~1s.

## Practical Patterns

### Timeout handling

```python
try:
    result = await asyncio.wait_for(fetch_data(url), timeout=5.0)
except asyncio.TimeoutError:
    print("Request timed out")
```

### Semaphore for rate limiting

```python
sem = asyncio.Semaphore(10)  # Max 10 concurrent requests

async def fetch_with_limit(url: str):
    async with sem:
        return await fetch_data(url)
```

## FastAPI Integration

FastAPI is built on asyncio. Any route defined with `async def` automatically benefits:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_one("SELECT * FROM users WHERE id = $1", user_id)
    return user
```

## Conclusion

Asyncio is not always the right tool — CPU-bound tasks still need threads or multiprocessing. But for I/O-bound workloads, it delivers significant throughput improvements with clean, readable code.
