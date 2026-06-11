from datetime import datetime

from django.db import migrations
from django.utils import timezone


POST_SLUG = 'privacy-first-http-log-analytics-pipeline-django-fluent-bit-s3-athena'


POST_BODY = """When an API is running in production, every request tells a small story.

A client sends a request. The backend receives it, validates it, calls internal services, talks to external APIs, waits for responses, handles errors, and finally returns something back to the client.

Most of the time, this flow works quietly in the background. But when something goes wrong, the first question is usually simple:

What happened to this request?

That question is not always easy to answer.

In a modern backend system, an API does not just receive requests and return responses. One incoming request can trigger several internal service calls, external partner API calls, validation checks, and background workflows. During daily operations, engineering teams need to answer questions like:

* Which API endpoints are returning the most errors?
* Which requests are slow?
* Which outgoing service calls are failing?
* Are failures caused by HTTP errors, timeouts, or connection issues?
* Can we follow one request from the moment it enters the system to the external calls it makes?

At the same time, logs can easily become dangerous.

If we log request bodies, response bodies, authentication headers, tokens, personal identifiers, or financial data, our logging system can quickly turn into a second database of sensitive information.

So the goal was not to log everything.

The goal was to log the right things:

* safe operational metadata,
* request and response status,
* request duration,
* outgoing service call details,
* error types,
* correlation IDs,
* enough context to debug production issues,
* without storing sensitive payloads.

To solve this, I built a structured HTTP logging layer inside a Django application and connected it to a low-cost analytics pipeline using Fluent Bit, Amazon S3, and Athena.

## The Idea

Instead of sending raw application logs to an expensive logging platform, the application writes clean JSON logs to stdout.

From there, the infrastructure takes over.

Fluent Bit collects the logs from Kubernetes, stores them in S3, and Athena lets us query them later with SQL.

```mermaid
flowchart TD
    Client[Client or External Service] --> Django[Django API]
    Django --> Middleware[HttpLoggingMiddleware<br/>incoming requests]
    Django --> HttpClient[LoggedHttpClient<br/>outgoing calls]
    Middleware --> Formatter[JsonFormatter]
    HttpClient --> Formatter
    Formatter --> Stdout[stdout container logs]
    Stdout --> FluentBit[Fluent Bit DaemonSet on EKS]
    FluentBit --> S3[(Amazon S3)]
    S3 --> Athena[Amazon Athena]
```

The Django app does not write directly to S3. It writes structured logs to stdout, which keeps the application simple and lets Kubernetes and Fluent Bit own log shipping.

## Application-Level Logging Design

The implementation is split into a small HTTP logging package:

* `HttpLoggingMiddleware` logs incoming Django requests.
* `LoggedHttpClient` logs outgoing HTTP requests.
* `JsonFormatter` serializes log records as single-line JSON.
* A request context helper stores the current `request_id` during the request lifecycle.
* A DRF exception helper attaches safe API error metadata to the underlying Django request.

The package emits three log types:

* `incoming_http`
* `outgoing_http`
* `service_error`

That `log_type` field gives Fluent Bit, S3, and Athena a simple way to filter and query records.

```mermaid
flowchart LR
    Package[HTTP logging package] --> Incoming[incoming_http]
    Package --> Outgoing[outgoing_http]
    Package --> ServiceError[service_error]
    Incoming --> Query[Filter in Athena]
    Outgoing --> Query
    ServiceError --> Query
```

## Incoming Request Logs

Incoming requests are logged by Django middleware after the response is ready.

The middleware either reuses the inbound `X-Request-ID` header or generates a new UUID. It then stores that ID on the request and in local request context so outgoing HTTP calls can inherit it.

Example incoming log:

```json
{
  "timestamp": "2026-06-11T10:15:30.123Z",
  "level": "INFO",
  "logger": "http_logging.incoming",
  "message": "POST /api/applications/",
  "log_type": "incoming_http",
  "direction": "incoming",
  "service": "api",
  "environment": "production",
  "request_id": "8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11",
  "method": "POST",
  "path": "/api/applications/",
  "status_code": 201,
  "duration_ms": 142.61,
  "remote_ip": "203.0.113.10",
  "user_agent": "Mozilla/5.0"
}
```

This single record already tells us:

* which endpoint was called,
* which method was used,
* how long it took,
* what status code was returned,
* which environment handled the request,
* which request ID can be used for tracing.

For 4xx and 5xx responses, the middleware adds safe error metadata:

```json
{
  "log_type": "incoming_http",
  "direction": "incoming",
  "request_id": "8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11",
  "method": "POST",
  "path": "/api/applications/",
  "status_code": 400,
  "duration_ms": 35.42,
  "error_message": "Bad Request",
  "error_code": "validation_error",
  "error_detail": "Invalid input on fields: application_id",
  "error_fields": {
    "application_id": ["Incorrect format"]
  }
}
```

The important detail is that validation logs include field names and schema-level error messages, not submitted field values.

So we can see that `application_id` failed validation, but we do not store the actual value the user submitted.

The middleware also skips noisy or low-value paths:

* `/health`
* `/metrics`
* `/favicon.ico`
* `/admin/`
* `/static/`
* `/media/`

This keeps the log volume focused on useful API traffic.

## Outgoing HTTP Logs

Incoming requests are only half of the story.

Many production issues happen when the API calls another service. That service may be slow, unavailable, return a bad response, or timeout.

For that part, outgoing HTTP calls use `LoggedHttpClient`, a `requests.Session` subclass. This keeps integration code familiar while adding structured logs automatically.

The current request ID is propagated as `X-Request-ID` on outgoing calls. This means the same ID can connect the incoming request with the external calls made during that request.

```mermaid
sequenceDiagram
    participant Client
    participant API as Django API
    participant Risk as Risk Service
    participant Partner as External Partner
    Client->>API: POST /api/applications<br/>X-Request-ID: 8f2...
    API->>Risk: POST /score<br/>X-Request-ID: 8f2...
    Risk-->>API: 200 OK
    API->>Partner: PUT /applications/123/status<br/>X-Request-ID: 8f2...
    Partner-->>API: Timeout
    API-->>Client: Response
```

Example outgoing log:

```json
{
  "timestamp": "2026-06-11T10:15:30.287Z",
  "level": "INFO",
  "logger": "http_logging.outgoing",
  "message": "Outgoing HTTP request",
  "log_type": "outgoing_http",
  "direction": "outgoing",
  "service": "api",
  "environment": "production",
  "target_service": "risk-service",
  "target_host": "risk.internal",
  "method": "POST",
  "url": "https://risk.internal/score",
  "duration_ms": 238.9,
  "request_id": "8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11",
  "status_code": 200
}
```

Now, when we investigate a request, we can see not only the incoming API call but also the internal or external services it depended on.

For failures, the client records the failure type without logging raw payloads:

```json
{
  "level": "ERROR",
  "logger": "http_logging.outgoing",
  "message": "Outgoing HTTP request failed",
  "log_type": "outgoing_http",
  "direction": "outgoing",
  "target_service": "external-partner",
  "target_host": "partner.example.com",
  "method": "PUT",
  "url": "https://partner.example.com/applications/123/status",
  "duration_ms": 95001.27,
  "request_id": "8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11",
  "error_type": "Timeout",
  "error_message": "The request timed out"
}
```

This makes timeout and connection problems visible without storing request bodies, response bodies, or credentials.

For JSON error responses, only a small allowlist of fields is extracted:

* `error.code`
* `error.message`
* `code`
* `message`
* `detail`
* `error_description`

Everything else in the response body is ignored.

That was an important design decision. Instead of trying to redact an entire unknown response body, we only read the few fields we know are safe and useful.

## Service Error Logs

Some external APIs return useful business-level error fields after a non-2xx response.

For that case, a separate service error log can be emitted.

Example:

```json
{
  "level": "WARNING",
  "logger": "http_logging.outgoing",
  "message": "External service error",
  "log_type": "service_error",
  "direction": "outgoing",
  "service": "api",
  "environment": "production",
  "target_service": "external-partner",
  "request_id": "8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11",
  "status_code": 400,
  "external_error_code": "INVALID_REQUEST",
  "external_error_message": "The request could not be processed"
}
```

This gives support and engineering teams useful diagnostics without storing the complete external service response.

## Privacy and Safety Rules

The most important part of this implementation is not the infrastructure. It is the safety contract in the application.

The logging layer follows these rules:

* request bodies are never logged,
* response bodies are never logged,
* authorization headers are never logged,
* cookies are never logged,
* query strings and URL fragments are stripped from outgoing URLs,
* sensitive logging context keys are silently dropped,
* error strings are truncated to keep log records bounded,
* logging failures never break the request or outgoing HTTP call.

Sensitive keys typically include authentication data, tokens, passwords, personal identifiers, bank account data, card data, names, emails, phone numbers, dates of birth, and addresses.

Fluent Bit, S3, and Athena are storage and query infrastructure. The application code is where we enforce what is safe to emit.

```mermaid
flowchart LR
    Payloads[Request bodies<br/>Response bodies<br/>Tokens<br/>Cookies] -. blocked .-> Stop[Not emitted]
    Safe[Status codes<br/>Durations<br/>Paths<br/>Request IDs<br/>Safe error metadata] --> Logs[Structured JSON logs]
    Logs --> Analytics[Analytics pipeline]
```

## JSON Formatting for Fluent Bit

The Django logging configuration uses a custom JSON formatter:

```python
"json": {
    "()": "http_logging.logging.JsonFormatter",
}
```

The HTTP logging logger writes to stdout:

```python
"http_logging_stdout": {
    "class": "logging.StreamHandler",
    "stream": "ext://sys.stdout",
    "formatter": "json",
}
```

Each record becomes one JSON object per line.

That makes Fluent Bit ingestion simple because container logs are already structured before they leave the pod.

## Why Fluent Bit, S3, and Athena?

Fluent Bit runs as a DaemonSet in EKS and collects logs from Kubernetes container log files:

```text
/var/log/containers/*.log
```

It can enrich records with Kubernetes metadata and ship them to S3.

S3 then becomes the durable, low-cost storage layer.

A typical partition layout looks like this:

```text
s3://http-logs/
  service=api/
    log_type=incoming_http/
      year=2026/
        month=06/
          day=11/
```

Partitioning by date, service, and log type keeps Athena queries cheaper because less data needs to be scanned.

```mermaid
flowchart TD
    Bucket[s3://http-logs/] --> Service[service=api]
    Service --> LogType[log_type=incoming_http]
    LogType --> Year[year=2026]
    Year --> Month[month=06]
    Month --> Day[day=11]
    Day --> Files[JSON log files]
    Athena[Athena query] --> LogType
```

## Querying Logs with Athena

Once the JSON logs are in S3, Athena can answer operational questions with SQL.

Top failing incoming endpoints:

```sql
SELECT
  path,
  status_code,
  COUNT(*) AS total
FROM http_logs
WHERE log_type = 'incoming_http'
  AND status_code >= 400
  AND year = '2026'
  AND month = '06'
  AND day = '11'
GROUP BY path, status_code
ORDER BY total DESC;
```

Slowest incoming endpoints:

```sql
SELECT
  path,
  approx_percentile(duration_ms, 0.95) AS p95_ms,
  avg(duration_ms) AS avg_ms,
  COUNT(*) AS total
FROM http_logs
WHERE log_type = 'incoming_http'
GROUP BY path
ORDER BY p95_ms DESC;
```

Outgoing service failures:

```sql
SELECT
  target_service,
  status_code,
  error_type,
  COUNT(*) AS total
FROM http_logs
WHERE log_type = 'outgoing_http'
  AND (status_code >= 400 OR error_type IS NOT NULL)
GROUP BY target_service, status_code, error_type
ORDER BY total DESC;
```

Trace a request across incoming and outgoing logs:

```sql
SELECT
  timestamp,
  log_type,
  direction,
  method,
  path,
  url,
  target_service,
  status_code,
  duration_ms,
  error_code,
  error_type
FROM http_logs
WHERE request_id = '8f2d4a7c-38d4-4f77-a2f6-08b64f0e3c11'
ORDER BY timestamp;
```

External service errors:

```sql
SELECT
  target_service,
  external_error_code,
  external_error_message,
  COUNT(*) AS total
FROM http_logs
WHERE log_type = 'service_error'
GROUP BY target_service, external_error_code, external_error_message
ORDER BY total DESC;
```

These queries make the logs useful during real incidents. We can quickly move from "something is failing" to "this endpoint is failing because this downstream service is returning this error."

```mermaid
flowchart LR
    Alert[Incident or alert] --> Query1[Find failing endpoint]
    Query1 --> Query2[Check downstream service failures]
    Query2 --> Trace[Trace request_id]
    Trace --> Cause[Identify likely cause]
```

## Lessons Learned

The biggest lesson is that useful HTTP observability does not require logging sensitive payloads.

A few design decisions made the system safer and easier to operate:

* Use structured JSON from the application instead of parsing free-form log text later.
* Add a `log_type` field so downstream tools can filter records cheaply.
* Generate or reuse `X-Request-ID` at the edge of the request lifecycle.
* Propagate the request ID into outgoing HTTP calls.
* Strip query strings from logged outgoing URLs.
* Keep error extraction allowlisted instead of trying to redact arbitrary response bodies.
* Treat caller-provided logging context as untrusted.
* Make logging best-effort so observability code cannot break production traffic.

## Conclusion

This setup gave us a practical way to understand production HTTP traffic without over-logging sensitive data.

The Django application decides what is safe to emit. Fluent Bit collects the logs from EKS. S3 stores them cheaply. Athena makes them searchable when we need to investigate an issue.

The biggest lesson from this implementation was that useful observability does not require logging everything.

If the logs contain the right metadata, a request ID, timing information, status codes, and safe error details, they are often enough to understand what happened in production without exposing private user data.
"""


def seed_privacy_first_http_log_analytics_blog(apps, schema_editor):
    BlogCategory = apps.get_model('portfolio', 'BlogCategory')
    BlogPost = apps.get_model('portfolio', 'BlogPost')
    Tag = apps.get_model('portfolio', 'Tag')

    category, _ = BlogCategory.objects.get_or_create(
        slug='backend-engineering',
        defaults={'name': 'Backend Engineering'},
    )

    post, _ = BlogPost.objects.update_or_create(
        slug=POST_SLUG,
        defaults={
            'title': 'Building a Privacy-First HTTP Log Analytics Pipeline with Django, Fluent Bit, S3, and Athena',
            'category': category,
            'excerpt': 'A practical walkthrough of structured HTTP logging in Django, safe request correlation, Fluent Bit log shipping, S3 storage, and Athena SQL analytics.',
            'body': POST_BODY,
            'status': 'published',
            'published_at': timezone.make_aware(datetime(2026, 6, 11, 9, 0)),
            'seo_title': 'Privacy-First HTTP Log Analytics Pipeline',
            'meta_description': 'Build privacy-first HTTP log analytics with Django structured logging, Fluent Bit, Amazon S3, and Athena without storing sensitive payloads.',
        },
    )

    tags = []
    for name, slug in (
        ('Backend Engineering', 'backend-engineering'),
        ('Observability', 'observability'),
        ('Django', 'django'),
        ('AWS', 'aws'),
        ('Privacy', 'privacy'),
    ):
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={'name': name})
        tags.append(tag)
    post.tags.set(tags)


class Migration(migrations.Migration):
    dependencies = [
        ('portfolio', '0009_seed_webhooks_vs_polling_blog'),
    ]

    operations = [
        migrations.RunPython(seed_privacy_first_http_log_analytics_blog, migrations.RunPython.noop),
    ]
