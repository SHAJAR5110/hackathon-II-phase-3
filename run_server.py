#!/usr/bin/env python
"""
Run the FastAPI server for the Todo Chatbot
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    # Change to the huggingface-backend directory so imports work
    os.chdir("C:\\Users\\HP\\Desktop\\H\\GIAIC\\phase 3\\huggingface-backend")

    # Add to Python path so src can be imported
    sys.path.insert(0, os.getcwd())

    # Run uvicorn
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ]
    )
