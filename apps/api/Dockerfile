# apps/api/Dockerfile
# SiapQuiz API + worker arq — satu image, dua entry point (uvicorn / arq).
# Base: python:3.12-slim. torch wajib varian CPU (DD-LIB-01).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1

# Pasang uv dari image resmi (bukan pip, biar konsisten dengan lockfile)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Salin manifest dulu agar layer cache bekerja saat dependensi tak berubah.
# --no-dev: produksi tidak butuh mypy/ruff/pytest (dihemat ±340MB).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# torch WAJIB varian CPU — varian default menarik CUDA (~2 GB) yang tak berguna
# di VPS tanpa GPU. Dipasang di luar uv sync karena bukan bagian dari lockfile
# (sengaja: uv sync akan menarik torch CUDA dari PyPI bila tercantum di pyproject).
RUN uv pip install torch --index-url https://download.pytorch.org/whl/cpu

# User non-root DIBUAT di awal, sebelum COPY kode. Jangan pernah
# `chown -R /app` setelah install torch/venv — Docker menyalin ulang seluruh
# direktori sebagai layer baru (menambah ~1 GB) hanya untuk mengubah ownership.
RUN useradd --create-home appuser \
    && mkdir -p /data/uploads /data/hfcache \
    && chown -R appuser:appuser /data

# Salin kode aplikasi (kepemilikan appuser langsung, tanpa chown -R)
COPY --chown=appuser:appuser app ./app
COPY --chown=appuser:appuser alembic.ini ./
COPY --chown=appuser:appuser alembic ./alembic
COPY --chown=appuser:appuser docker-entrypoint.sh ./
RUN chmod +x docker-entrypoint.sh

# Binari venv (uvicorn, alembic, arq) harus ada di PATH untuk user non-root
ENV PATH="/app/.venv/bin:$PATH"
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
