from app.core.config import settings


def setup_azure_monitor(app):
    """Hook up OTel tracing + metrics if APPLICATIONINSIGHTS_CONNECTION_STRING is set."""
    connection_string = settings.applicationinsights_connection_string

    if not connection_string:
        print("Azure Monitor disabled (no connection string)")
        return

    from azure.monitor.opentelemetry.exporter import (
        AzureMonitorTraceExporter,
        AzureMonitorMetricExporter,
    )
    from opentelemetry import trace, metrics
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    trace_exporter = AzureMonitorTraceExporter(
        connection_string=connection_string
    )
    tracer_provider = TracerProvider()
    tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(tracer_provider)

    # Metrics export
    metric_exporter = AzureMonitorMetricExporter(
        connection_string=connection_string
    )
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter, export_interval_millis=60000
    )
    meter_provider = MeterProvider(metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    FastAPIInstrumentor.instrument_app(app)

    print("Azure Monitor initialized")
