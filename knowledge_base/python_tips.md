# Python Tips & Best Practices

## Virtual Environments
Always use virtual environments for Python projects. Create one with:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```
This isolates project dependencies and prevents conflicts between packages.

## Type Hints
Use type hints to improve code readability and catch bugs early:
```python
def greet(name: str, age: int) -> str:
    return f"Hello {name}, you are {age} years old."
```
Run `mypy` for static type checking in your CI pipeline.

## List Comprehensions
Prefer list comprehensions over loops for simple transformations:
```python
# Good
squared = [x**2 for x in range(10)]

# Avoid
squared = []
for x in range(10):
    squared.append(x**2)
```

## Context Managers
Use context managers for resource management:
```python
with open("data.txt", "r") as f:
    content = f.read()
# File is automatically closed
```

## Error Handling
Be specific with exceptions — never use bare `except`:
```python
# Good
try:
    value = int(user_input)
except ValueError:
    print("Please enter a valid number")

# Bad
try:
    value = int(user_input)
except:
    pass
```

## F-Strings
Use f-strings for readable string formatting (Python 3.6+):
```python
name = "Alice"
age = 30
print(f"{name} is {age} years old")
```

## Dataclasses
Use dataclasses for structured data:
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
    email: str
```

## Async Programming
For I/O-bound tasks, use `asyncio`:
```python
import asyncio

async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```
