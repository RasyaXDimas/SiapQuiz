#!/bin/sh
set -e

# Jalankan migrasi dulu, lalu eksekusi perintah yang diberikan (uvicorn / arq).
# Container api dan worker berbagi image ini; keduanya menjalankan alembic
# upgrade head yang idempoten (lock table di dalam alembic_version).
alembic upgrade head

exec "$@"
