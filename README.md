<h3 align="center">qr.spoo.me</h3>
<p align="center">Open-Source QR Code API</p>

<p align="center">
    <a href="#-features"><kbd>Features</kbd></a>
    <a href="#-endpoints"><kbd>Endpoints</kbd></a>
    <a href="https://qr.spoo.me/docs" target="_blank"><kbd>API Docs</kbd></a>
    <a href="#-getting-started"><kbd>Getting Started</kbd></a>
    <a href="#-contributing"><kbd>Contributing</kbd></a>
</p>

<p align="center">
<a href="https://github.com/spoo-me/qr"><img src="https://img.shields.io/github/stars/spoo-me/qr?style=flat&color=6a5cf4" alt="Stars"></a>
<a href="https://github.com/spoo-me/qr/actions"><img src="https://github.com/spoo-me/qr/actions/workflows/tests.yaml/badge.svg" alt="Tests"></a>
<a href="https://spoo.me/discord"><img src="https://img.shields.io/discord/1192388005206433892?logo=discord" alt="Discord"></a>
<a href="https://twitter.com/spoo_me"><img src="https://img.shields.io/twitter/follow/spoo_me?logo=x&label=%40spoo_me&color=0bf" alt="X (formerly Twitter) Follow"></a>
</p>

# Introduction

**qr.spoo.me** is the QR code generation sub-service of [spoo.me](https://spoo.me). It provides a fast, free, open-source API for generating styled QR codes with support for multiple output formats, gradient coloring, logo embedding, and batch generation.

# Features

- `Classic QR Codes` - Solid fill and background colors with customizable module styles
- `Gradient QR Codes` - Vertical, horizontal, radial, and square gradient coloring
- `6 Module Styles` - Rounded, square, circle, gapped, horizontal bars, vertical bars
- `SVG & PNG Output` - Choose between raster and vector formats
- `Logo Embedding` - Embed a logo image in the center of any QR code
- `Batch Generation` - Generate up to 20 QR codes in a single request (ZIP archive)
- `Fully Async` - Non-blocking I/O with CPU-bound work offloaded to thread pool
- `Open Source` - Free to use and self-host

# Endpoints

All API endpoints are under `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET/POST` | `/api/v1/classic` | Generate a classic QR code |
| `POST` | `/api/v1/classic/logo` | Classic QR code with embedded logo |
| `GET/POST` | `/api/v1/gradient` | Generate a gradient QR code |
| `POST` | `/api/v1/gradient/logo` | Gradient QR code with embedded logo |
| `POST` | `/api/v1/batch` | Batch generate up to 20 QR codes (ZIP) |
| `GET/POST` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |

## Classic QR Code

```bash
curl "https://qr.spoo.me/api/v1/classic?text=https://spoo.me&fill=%23000000&back=%23ffffff&module_style=rounded" \
  --output qr.png
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | *required* | Text or URL to encode |
| `fill` | string | `black` | Fill color (name, hex, or RGB) |
| `back` | string | `white` | Background color |
| `size` | int | auto | Output size in pixels (10–1000) |
| `module_style` | string | `rounded` | `rounded`, `square`, `circle`, `gapped`, `horizontal_bars`, `vertical_bars` |
| `output_format` | string | `png` | `png` or `svg` |
| `format` | string | — | Structured data format (see below) |
| `formattings` | string | — | JSON-encoded parameters for the data format |

## Gradient QR Code

```bash
curl "https://qr.spoo.me/api/v1/gradient?text=https://spoo.me&gradient1=(106,26,76)&gradient2=(64,53,60)&gradient_type=vertical" \
  --output qr_gradient.png
```

**Additional parameters** (on top of classic):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gradient1` | string | `(106,26,76)` | Inner/start gradient color (RGB) |
| `gradient2` | string | `(64,53,60)` | Outer/end gradient color (RGB) |
| `gradient_type` | string | `vertical` | `vertical`, `horizontal`, `radial`, `square` |

## Logo Embedding

```bash
curl -X POST "https://qr.spoo.me/api/v1/classic/logo?text=https://spoo.me" \
  -F "logo=@logo.png" \
  --output qr_with_logo.png
```

## Batch Generation

```bash
curl -X POST "https://qr.spoo.me/api/v1/batch" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"text": "https://spoo.me"}, {"text": "https://github.com", "fill": "#FF0000"}]}' \
  --output qrcodes.zip
```

# Getting Started

<details>

<summary>Expand this for a Quick Start</summary>

## Method 1 — Docker (Recommended)

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)

### Clone and run

```bash
git clone https://github.com/spoo-me/qr.git
cd qr
cp .env.example .env
docker compose up -d --build
```

The API will be available at `http://localhost:8080`.

## Method 2 — Manual

### Prerequisites

- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

### Clone the repository

```bash
git clone https://github.com/spoo-me/qr.git
cd qrcode-api
```

### Install dependencies

```bash
uv sync
```

### Configure environment

```bash
cp .env.example .env
```

### Start the server

```bash
uv run uvicorn main:app --reload --no-access-log
```

The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Run tests

```bash
uv run python -m pytest
```

</details>

# Architecture

```
qr/
├── main.py                    # Uvicorn entry point
├── app.py                     # FastAPI application factory
├── config.py                  # pydantic-settings configuration
├── errors.py                  # Typed error hierarchy
├── routes/
│   ├── api_v1/                # /api/v1 endpoints
│   │   ├── classic.py         # Classic QR generation
│   │   ├── gradient.py        # Gradient QR generation
│   │   └── batch.py           # Batch generation
│   ├── health_routes.py       # /health
│   └── page_routes.py         # / (web UI)
├── services/
│   └── qr_service.py          # Async business logic (thread-pooled)
├── schemas/
│   ├── enums.py               # DataFormat, ModuleStyle, GradientType, OutputFormat
│   └── dto/                   # Request/response Pydantic models
├── shared/
│   ├── color.py               # Color parsing
│   ├── formatters.py          # vCard, WiFi, iCal, etc.
│   ├── qr_utils.py            # QR version/box size calculators
│   ├── logging.py             # structlog configuration
│   └── ip_utils.py            # Client IP extraction
├── dependencies/
│   └── services.py            # FastAPI Depends() providers
├── middleware/
│   ├── error_handler.py       # Global exception handlers
│   ├── logging.py             # Request logging (request_id, duration)
│   └── openapi.py             # OpenAPI schema configuration
├── tests/                     # Unit + integration tests
├── dockerfile                 # uv-based Docker build
├── docker-compose.yml         # Dev compose
└── pyproject.toml             # uv project config
```

# Contributing

Contributions are always welcome! Here's how you can contribute:

- Bugs are logged using the GitHub issue system. To report a bug, simply [open a new issue](https://github.com/spoo-me/qr/issues/new).
- Make a [pull request](https://github.com/spoo-me/qr/pulls) for any feature or bug fix.

> [!IMPORTANT]
> For any type of support or queries, feel free to reach out to us at <kbd>[support@spoo.me](mailto:support@spoo.me)</kbd>

---

<h6 align="center">
<img src="https://spoo.me/static/images/favicon.png" height=30 title="Spoo.me Copyright">
<br>
&copy; spoo.me . 2026

All Rights Reserved</h6>

<p align="center">
 <a href="https://github.com/spoo-me/qr/blob/main/LICENSE"><img src="https://img.shields.io/static/v1.svg?style=for-the-badge&label=License&message=APACHE-2.0&logoColor=d9e0ee&colorA=363a4f&colorB=b7bdf8"/></a>
</p>
