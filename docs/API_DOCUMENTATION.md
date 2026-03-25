# API Documentation

This document describes the API implemented in this repository today.

Base URL for local development: `http://localhost:5000`

## Authentication

Authentication is optional and controlled by `ENABLE_AUTH`.

- When `ENABLE_AUTH=false`: no API key is required.
- When `ENABLE_AUTH=true`: `POST /api/v1/hello` requires `X-API-Key`.

Required header when auth is enabled:

```text
X-API-Key: <your-api-key>
```

## Endpoints

### GET `/health`

Returns basic service status.

Example response:

```json
{
  "status": "healthy",
  "service": "python-devops-reference-app",
  "version": "1.0.0",
  "metrics": {
    "cpu_percent": 12.0,
    "memory_percent": 41.5,
    "disk_percent": 70.1
  }
}
```

`metrics` is included when monitoring is enabled and metric collection succeeds.

### GET `/health/ready`

Readiness probe.

```json
{ "ready": true }
```

### GET `/health/live`

Liveness probe.

```json
{ "alive": true }
```

### GET `/api/v1/hello/<name>`

Returns a greeting message.

Rules:

- `name` must not be blank
- max length: 100 characters

Example:

```bash
curl http://localhost:5000/api/v1/hello/World
```

Response:

```json
{
  "message": "Hello, World!",
  "timestamp": "2026-03-25T12:00:00.000000"
}
```

### POST `/api/v1/hello`

Accepts JSON payload and returns a greeting.

Request body:

```json
{
  "name": "Alice"
}
```

Example:

```bash
curl -X POST http://localhost:5000/api/v1/hello \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Alice\"}"
```

Possible status codes:

- `200` valid request
- `400` invalid payload (missing/empty/too long name)
- `401` missing API key when auth is enabled
- `403` invalid API key when auth is enabled

### GET `/api/v1/info`

Returns app metadata.

Example response:

```json
{
  "app": "python-devops-reference-app",
  "version": "1.0.0",
  "environment": "unknown",
  "debug": true,
  "auth_enabled": false
}
```

## Rate limiting

Rate limiting is configured through Flask-Limiter and environment config:

- Development: `100/hour`
- Staging: `500/hour`
- Production: `1000/hour`

## Error shape

Most error responses follow:

```json
{
  "error": "message"
}
```

Validation errors from Pydantic include a `details` array.
