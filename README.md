# FastAPI - Base Project (Modular)

This is a minimal base project structure for a scalable FastAPI application organized per-module.

Run locally:

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Structure highlights:

- `app/main.py`: application factory / entrypoint
- `app/api/v1/*`: versioned routers (example `users.py`)
- `app/schemas/`: pydantic models
- `app/services/`: business logic per module (replace with repos/DB services)
- `app/db/`: db connection placeholders
- `app/core/config.py`: configuration via environment

Next steps:

- Replace in-memory `UserService` with actual DB calls (e.g., Motor for MongoDB)
- Add authentication, dependency injection in `app/api/deps.py` if needed
- Add tests, CI, and deployment manifest
