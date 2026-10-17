from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS: allow any website (including the grader page) to call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- The four layers (lowest to highest priority) ----
DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

YAML_LAYER = {
    "port": 8312,
    "workers": 2,
    "log_level": "debug",
    "api_key": "key-cje4j22kf9",
}

DOTENV_LAYER = {
    "APP_PORT": "8199",
    "NUM_WORKERS": "14",      # alias for workers
    "APP_LOG_LEVEL": "debug",
}

OS_ENV_LAYER = {
    "APP_PORT": "8098",
    "APP_WORKERS": "2",
    "APP_API_KEY": "key-1ew0tw9xj0",
}


def normalize(raw: dict) -> dict:
    """Turn APP_PORT -> port, NUM_WORKERS -> workers, etc."""
    out = {}
    for key, value in raw.items():
        k = key.lower()
        if k.startswith("app_"):
            k = k[4:]
        if k == "num_workers":
            k = "workers"
        out[k] = value
    return out


def coerce(key: str, value):
    """Convert values to the right type."""
    if key in ("port", "workers"):
        return int(value)
    if key == "debug":
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("true", "1", "yes", "on")
    return str(value)


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):
    config = dict(DEFAULTS)                       # 1. defaults
    config.update(YAML_LAYER)                     # 2. yaml
    config.update(normalize(DOTENV_LAYER))        # 3. .env
    config.update(normalize(OS_ENV_LAYER))        # 4. OS env

    # 5. CLI overrides: ?set=key=value (split on FIRST "=" only)
    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            config[k.strip().lower()] = v

    # Fix types
    result = {k: coerce(k, v) for k, v in config.items()}

    # Hide the secret
    result["api_key"] = "****"
    return result