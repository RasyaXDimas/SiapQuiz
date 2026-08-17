# SiapQuiz

Mengubah materi ajar dosen (PDF/DOCX/PPTX) menjadi kuis pilihan ganda yang dikerjakan siswa secara online real-time dengan leaderboard.

**Janji inti produk:** setiap soal membawa kutipan sumber terverifikasi dari dokumen dosen sendiri. Soal yang kutipannya tidak bisa ditemukan di sumber dibuang otomatis, sebelum pernah dilihat guru.

## Arsitektur

Monolith modular, tiga proses aplikasi, satu basis kode, dijalankan dengan Docker Compose (image identik untuk lokal dan VPS).

```
apps/
├── api/    # FastAPI + worker arq (Python 3.12, satu paket)
└── web/    # Next.js App Router (TypeScript, Tailwind, shadcn/ui)
```

| Service | Peran |
|---|---|
| `caddy` | Reverse proxy, TLS otomatis, upgrade WebSocket |
| `web` | Frontend Next.js |
| `api` | API FastAPI (stateless, bisa di-scale) |
| `worker` | Antrean job arq (embedding + panggilan LLM BYOK) |
| `postgres` | PostgreSQL 16 + pgvector |
| `redis` | Antrean job, pub/sub realtime, leaderboard |

Dokumentasi lengkap ada di `project-docs/`. **Baca `project-docs/06-ai-context/AGENTS.md` dulu** sebelum bekerja — itu kontrak untuk setiap agent/developer.

## Prasyarat

- Docker Engine + Docker Compose v2
- Git
- ~10 GB ruang disk (image + model embedding + volume)

## Menjalankan

```bash
# 1. Siapkan environment
cp .env.example .env
# Buka .env dan isi minimal tiga nilai berikut:
#   POSTGRES_PASSWORD  — bebas
#   JWT_SECRET         — openssl rand -hex 32
#   BYOK_MASTER_KEY    — openssl rand -hex 32

# 2. Bangun dan jalankan semua service
docker compose up --build
```

Unduhan pertama memakan waktu beberapa menit karena image `api`/`worker` memasang torch CPU (varian tanpa CUDA, `DD-LIB-01`) dan mengunduh model embedding (~120 MB, disimpan di volume `hfcache` sehingga hanya sekali).

### Verifikasi

```bash
curl http://localhost/api/v1/health     # {"status":"ok",...}
curl http://localhost/api/v1/ready      # checks.postgres & checks.redis = true
docker compose logs worker | grep worker.started
```

Buka `http://localhost` — halaman landing tampil.

### Migrasi database

Dijalankan otomatis saat container `api` start. Untuk manual:

```bash
docker compose exec api uv run alembic upgrade head
docker compose exec api uv run alembic current
```

### Perintah harian

```bash
docker compose logs -f api worker       # ikuti log
docker compose restart api              # setelah ubah env
docker compose exec api uv run pytest   # jalankan test backend
docker compose down                     # hentikan (volume TETAP ada)
```

> ⚠️ `docker compose down -v` **menghapus volume**, termasuk seluruh database dan dokumen yang diunggah. Jangan jalankan kecuali memang bermaksud memulai dari nol.

## Tooling mutu kode

```bash
# Backend (apps/api)
uv run ruff check . && uv run ruff format --check .
uv run mypy app
uv run pytest

# Frontend (apps/web)
pnpm lint && pnpm exec tsc --noEmit
```

CI (`.github/workflows/ci.yml`) menjalankan keduanya di setiap push.

## Struktur

```
apps/
├── api/                    # FastAPI + arq worker
│   ├── app/
│   │   ├── main.py         # entry FastAPI
│   │   ├── worker.py       # entry arq
│   │   ├── core/           # config, db, logging, errors, redis
│   │   ├── api/v1/         # router per domain
│   │   ├── tasks/          # fungsi arq
│   │   └── scripts/        # skrip operasional manual
│   ├── alembic/            # migrasi database
│   └── tests/
├── web/                    # Next.js App Router
│   └── src/{app,components,lib,hooks,stores}
└── legacy/                 # ARSIP read-only — tidak diimpor, tidak dimodifikasi
```

Dokumen acuan utama: `project-docs/` (PRD, system design, api-spec, coding standard, env config, KANBAN).
