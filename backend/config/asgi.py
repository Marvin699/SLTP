"""
ASGI config for the Smart Low-Altitude Emergency Transportation Teaching Platform.

Mounts both Django and FastAPI:
- Django handles /admin/ and any future Django routes
- FastAPI (path-planning agent) handles /api/path-planning/*
"""

import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# Ensure the backend directory is in the Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application
django_app = get_asgi_application()

# Initialize FastAPI application for path-planning agent
# We import after Django setup to avoid circular imports
try:
    from app.main import app as fastapi_app, _init_default_case
    path_planning_app = fastapi_app
    # 手动触发初始化（raw ASGI 挂载不会自动触发 lifespan）
    _init_default_case()
except ImportError as e:
    print(f"[ASGI] Warning: Could not import path_planning FastAPI app: {e}")
    print("[ASGI] Path Planning Agent API will not be available.")
    path_planning_app = None


async def application(scope, receive, send):
    """
    Main ASGI application that routes requests to Django or FastAPI.
    """
    if scope["type"] == "http" or scope["type"] == "websocket":
        path = scope.get("path", "")

        # Route path-planning requests to FastAPI
        if path.startswith("/api/path-planning"):
            if path_planning_app is not None:
                # Strip the prefix before passing to FastAPI
                root_path = scope.get("root_path", "")
                scope = dict(scope)
                scope["root_path"] = root_path + "/api/path-planning"
                # Remove the prefix from the path
                scope["path"] = path[len("/api/path-planning"):] or "/"
                await path_planning_app(scope, receive, send)
                return

        # Everything else goes to Django
        await django_app(scope, receive, send)
    else:
        # For non-http/websocket (lifespan, etc.), delegate to Django
        await django_app(scope, receive, send)
