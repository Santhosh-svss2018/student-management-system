"""
Simple entrypoint to start the EduManage FastAPI development server with Uvicorn.
Run with: python run.py
"""

import uvicorn

if __name__ == "__main__":
    print("Starting EduManage FastAPI Backend Server on http://127.0.0.1:8000 ...")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
