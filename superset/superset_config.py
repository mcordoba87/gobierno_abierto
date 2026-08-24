import os
from cachelib.redis import RedisCache

FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "DASHBOARD_RBAC": True,
}

REDIS_HOST = "redis"
REDIS_PORT = 6379
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/0"

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_cache_",
    "CACHE_REDIS_URL": REDIS_URL,
}

RESULTS_BACKEND = RedisCache(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    key_prefix="superset_results_",
)

SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://superset:{os.getenv('POSTGRES_PASSWORD')}@db:5432/superset"
)

TIMEZONE = "America/Argentina/Cordoba"