#!/usr/bin/env python
"""
Run the FastAPI server for the Todo Chatbot
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    os.chdir("C:\\Users\\HP\\Desktop\\H\\GIAIC\\phase 3")

    # Run uvicorn
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.src.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
        ]
    )
