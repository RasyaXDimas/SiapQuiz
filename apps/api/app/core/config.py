"""Konfigurasi aplikasi SiapQuiz.

Seluruh nilai yang bisa berubah antara lokal dan produksi, atau yang mungkin
dikalibrasi, wajib ada di sini — tidak ada nilai hardcode di kode
(coding-standard.md §3.7). Daftar lengkap: project-docs/09-ops/env-config.md.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Inti aplikasi ---
    app_env: str = "development"  # development | production
    app_version: str = "0.1.0"
    log_level: str = "INFO"  # DEBUG hanya di lokal
    api_base_url: str = "http://localhost"  # dibaca frontend saat build & runtime
    cors_allowed_origins: str = "http://localhost,http://localhost:3000"

    # --- Database ---
    postgres_user: str = "siapquiz"
    postgres_password: str = "ganti-password-ini"
    postgres_db: str = "siapquiz"
    database_url: str = "postgresql+asyncpg://siapquiz:ganti-password-ini@postgres:5432/siapquiz"
    db_pool_size: int = 10  # per replica
    db_max_overflow: int = 10
    db_pool_timeout: int = 30  # detik
    postgres_max_connections: int = 150

    # --- Redis ---
    redis_url: str = "redis://redis:6379/0"
    redis_max_memory: str = "256mb"

    # --- Keamanan & token ---
    jwt_secret: str = "dummy-ganti-dengan-32-byte-acak"
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    participant_token_ttl_hours: int = 12
    cookie_secure: bool = False  # true di produksi
    cookie_samesite: str = "lax"
    byok_master_key: str = "dummy-32-byte-hex-ganti-ini"  # AES-256-GCM, rahasia kritis

    # --- Unggahan & batasan ---
    upload_dir: str = "/data/uploads"
    max_upload_mb: int = 25
    max_documents_per_org: int = 50
    allowed_upload_extensions: str = ".pdf,.docx,.pptx,.txt"

    # --- RAG & embedding ---
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    embedding_batch_size: int = 32
    hf_home: str = "/data/hfcache"
    chunk_max_chars: int = 500
    chunk_overlap_chars: int = 50
    retrieval_top_k: int = 5
    retrieval_min_similarity: float = 0.35

    # --- LLM & biaya ---
    llm_questions_per_call: int = 5
    llm_max_retries: int = 1
    llm_max_concurrency: int = 2
    llm_request_timeout_seconds: int = 120
    llm_backoff_max_attempts: int = 5
    generation_cache_ttl_days: int = 30
    default_budget_cap_usd: float = 0.50
    usd_to_idr_rate: int = 16000

    # --- Gate anti-halusinasi (inti produk) ---
    grounding_quote_threshold: float = 0.85
    grounding_answer_overlap_min: float = 0.30
    quality_score_threshold: int = 70
    prompt_version: str = "v1.0"

    # --- Sesi kuis ---
    leaderboard_broadcast_throttle_ms: int = 1000
    ws_heartbeat_interval_seconds: int = 20
    ws_idle_timeout_seconds: int = 90
    session_max_participants: int = 300

    # --- Rate limit ---
    ratelimit_login: str = "10/15minutes"
    ratelimit_generation_job: str = "20/hour"
    ratelimit_session_join: str = "30/minute"

    # --- Observability ---
    sentry_dsn: str = ""  # kosong = Sentry mati
    sentry_traces_sample_rate: float = 0.1

    # --- Produksi (khusus VPS) ---
    domain: str = ""
    acme_email: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",")]

    @property
    def upload_extensions_list(self) -> list[str]:
        return [ext.strip() for ext in self.allowed_upload_extensions.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
