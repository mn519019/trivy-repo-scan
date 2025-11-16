from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import subprocess
import tempfile
import shutil
import re
import os

load_dotenv()
FRONTEND_PATH = os.getenv("FRONTEND_PATH")

app = FastAPI()
# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve index.html at root
@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_PATH)

@app.get("/favicon.ico")
def favicon():
    return FileResponse(FRONTEND_PATH)

@app.post("/scan")
def scan_repo(repo_url: str = Form(...)):
    temp_dir = tempfile.mkdtemp()
    try:
        # Run Trivy with quiet mode for clean JSON
        result = subprocess.run(
            # ["trivy", "repo", repo_url, "--format", "json", "--quiet"],
            ["trivy", "repo", repo_url, "--format", "json"],
            capture_output=True,
            text=True
        )

        # Extract JSON from stdout (ignore logs)
        json_match = re.search(r"\{.*\}", result.stdout, re.DOTALL)
        scan_result = json_match.group(0) if json_match else "{}"

        return {
            "scan_result": scan_result,
            "logs": result.stderr,
            "exit_code": result.returncode
        }

    except subprocess.CalledProcessError as e:
        return {
            "error": str(e),
            "logs": e.stderr if e.stderr else "No logs available"
        }
    finally:
        shutil.rmtree(temp_dir)
