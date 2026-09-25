"""
FastAPI Hello World Example
Basic endpoints with different HTTP methods
"""

from fastapi import FastAPI
from datetime import datetime
from typing import Optional

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint - simple greeting"""
    return {"message": "Hello, World!", "framework": "FastAPI"}


@app.get("/about")
def read_about():
    """About page with student info"""
    return {
        "name": "[Your Name]",
        "course": "Web Programming",
        "university": "BFU"
    }


@app.get("/time")
def read_time():
    """Current time endpoint"""
    now = datetime.now()
    return {
        "current_time": now.strftime('%Y-%m-%d %H:%M:%S'),
        "timestamp": now.timestamp()
    }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    """Example with path parameter and query parameter"""
    return {
        "item_id": item_id,
        "q": q
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
