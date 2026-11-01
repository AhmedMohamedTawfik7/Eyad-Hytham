"""Azure Functions v2 ASGI entry point; local development can run wasla_api.main:app."""
import sys
from pathlib import Path

import azure.functions as func

sys.path.insert(0, str(Path(__file__).parent / "src"))
from wasla_api.main import app

function_app = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
