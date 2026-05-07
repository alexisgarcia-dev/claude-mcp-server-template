"""OpenTelemetry setup with HTTPX instrumentation and header masking.

Configures TracerProvider, OTLP exporter, and HTTPXClientInstrumentor.
Authorization header masking prevents API key leakage into trace backends.

See: docs/design-v0.1.0.md §5
"""

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.httpx import RequestInfo
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

from src.config import Settings


async def _mask_auth_header(span: object, request_info: RequestInfo) -> None:
    """Mask Authorization header in OTel spans to prevent API key leakage."""
    if request_info.headers and "authorization" in request_info.headers:
        span.set_attribute(  # type: ignore[attr-defined]
            "http.request.header.authorization", "***MASKED***"
        )


def setup_telemetry(config: Settings) -> TracerProvider | None:
    """Initialize OTel TracerProvider with OTLP exporter and HTTPX instrumentation.

    Returns TracerProvider for graceful shutdown in server lifespan.
    Returns None when telemetry is disabled (dev/test shortcut).
    """
    if not config.telemetry.enabled:
        return None

    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

    resource = Resource({"service.name": config.telemetry.service_name})
    sampler = TraceIdRatioBased(config.telemetry.sampling_ratio)
    provider = TracerProvider(resource=resource, sampler=sampler)

    exporter = OTLPSpanExporter(endpoint=config.telemetry.otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    HTTPXClientInstrumentor().instrument(async_request_hook=_mask_auth_header)

    return provider
