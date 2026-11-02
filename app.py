"""Start the Wasla API and web app for local development."""

from __future__ import annotations

import argparse
import os
import secrets
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parent
API_SOURCE = ROOT / "services" / "wasla-api" / "src"
WEB_ROOT = ROOT / "services" / "wasla-web"
NODE_MODULES = WEB_ROOT / "node_modules"
VITE_CLI = WEB_ROOT / "node_modules" / "vite" / "bin" / "vite.js"
WEB_PACKAGES = (
    "react",
    "react-dom",
    "react-router-dom",
    "@fluentui/react-components",
    "@fluentui/react-icons",
)
HOST = "127.0.0.1"
API_PORT = 8000
WEB_PORT = 5173
STARTUP_TIMEOUT = 90


def missing_prerequisites() -> list[str]:
    missing = []
    for module in ("fastapi", "sqlalchemy", "uvicorn"):
        try:
            __import__(module)
        except ImportError:
            missing.append(f"Python package is missing: {module}")

    if shutil.which("node") is None:
        missing.append("Node.js is not installed or is not on PATH.")
    if not VITE_CLI.is_file():
        missing.append("Frontend dependencies are not installed (Vite was not found).")
    for package in WEB_PACKAGES:
        package_json = NODE_MODULES.joinpath(*package.split("/"), "package.json")
        if not package_json.is_file():
            missing.append(f"Frontend dependency is missing: {package}")
    return missing


def available_port(preferred: int) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            listener.bind((HOST, preferred))
            return preferred
        except OSError:
            listener.bind((HOST, 0))
            return listener.getsockname()[1]


def configure_local_environment(api_port: int, web_port: int) -> None:
    os.environ.setdefault("APP_ENV", "development")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./wasla.db")
    if not os.environ.get("JWT_SECRET"):
        os.environ["JWT_SECRET"] = secrets.token_urlsafe(48)
    os.environ.setdefault("OPERATOR_EMAILS", "operator@example.test")
    os.environ["CORS_ORIGINS"] = (
        f"http://localhost:{web_port},http://127.0.0.1:{web_port}"
    )
    os.environ["VITE_API_URL"] = f"http://{HOST}:{api_port}"


def wait_for_service(
    name: str,
    url: str,
    process: subprocess.Popen[bytes],
) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(f"{name} exited with code {return_code}; see its output above.")
        try:
            with urlopen(url, timeout=1):
                return
        except (OSError, URLError):
            time.sleep(0.25)
    raise RuntimeError(f"{name} did not become ready within {STARTUP_TIMEOUT} seconds.")


def wait_for_port(
    name: str,
    host: str,
    port: int,
    process: subprocess.Popen[bytes],
) -> None:
    deadline = time.monotonic() + STARTUP_TIMEOUT
    while time.monotonic() < deadline:
        return_code = process.poll()
        if return_code is not None:
            raise RuntimeError(f"{name} exited with code {return_code}; see its output above.")
        try:
            with socket.create_connection((host, port), timeout=1):
                return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError(f"{name} did not open port {port} within {STARTUP_TIMEOUT} seconds.")


def stop_processes(processes: list[tuple[str, subprocess.Popen[bytes]]]) -> None:
    for _, process in reversed(processes):
        if process.poll() is None:
            process.terminate()
    for name, process in reversed(processes):
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            print(f"Force-stopped {name}.")


def run_app() -> int:
    missing = missing_prerequisites()
    if missing:
        print("Wasla cannot start because prerequisites are missing:")
        for item in missing:
            print(f"  - {item}")
        print("\nFrom the repository root, install them with:")
        print(f'  "{sys.executable}" -m pip install -r services/wasla-api/requirements.txt')
        print("  npm --prefix services/wasla-web install")
        return 1

    jwt_secret = os.environ.get("JWT_SECRET", "")
    if jwt_secret and len(jwt_secret) < 32:
        print(
            "JWT_SECRET must be at least 32 characters. "
            "Unset it for a temporary local secret or provide a longer value.",
            file=sys.stderr,
        )
        return 1

    api_port = available_port(API_PORT)
    web_port = available_port(WEB_PORT)
    configure_local_environment(api_port, web_port)

    processes: list[tuple[str, subprocess.Popen[bytes]]] = []
    try:
        api = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "wasla_api.main:app",
                "--app-dir",
                str(API_SOURCE),
                "--host",
                HOST,
                "--port",
                str(api_port),
            ],
            cwd=ROOT,
        )
        processes.append(("API", api))
        wait_for_service("API", f"http://{HOST}:{api_port}/api/health", api)

        web = subprocess.Popen(
            [
                shutil.which("node") or "node",
                str(VITE_CLI),
                "--host",
                HOST,
                "--port",
                str(web_port),
                "--strictPort",
            ],
            cwd=WEB_ROOT,
        )
        processes.append(("Web app", web))
        wait_for_port("Web app", HOST, web_port, web)

        print("\nWasla is running locally:")
        print(f"  Web app: http://{HOST}:{web_port}")
        print(f"  API docs: http://{HOST}:{api_port}/docs")
        print("Press Ctrl+C to stop both services.")
        while True:
            for name, process in processes:
                return_code = process.poll()
                if return_code is not None:
                    raise RuntimeError(f"{name} exited with code {return_code}.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping Wasla...")
        return 0
    except (OSError, RuntimeError) as error:
        print(f"\nWasla could not continue: {error}", file=sys.stderr)
        return 1
    finally:
        stop_processes(processes)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Wasla app locally.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="check whether the local Python and Node.js prerequisites are installed",
    )
    args = parser.parse_args()
    if args.check:
        missing = missing_prerequisites()
        if missing:
            print("\n".join(missing), file=sys.stderr)
            return 1
        print("Python, Node.js, and frontend dependencies are ready.")
        return 0
    return run_app()


if __name__ == "__main__":
    raise SystemExit(main())
