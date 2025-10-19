import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

def setup_opentelemetry(service_name: str = "microsoft-agent-framework-fdh"):
    """Configure OpenTelemetry for enterprise monitoring"""
    
    # Create resource with service attributes
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: service_name,
        ResourceAttributes.SERVICE_VERSION: "1.0.0",
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: os.getenv("ENVIRONMENT", "development"),
    })
    
    # Set up the tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    
    # Configure OTLP exporter (for Jaeger, Tempo, etc.)
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    
    # Add batch span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # Auto-instrument popular libraries
    FastAPIInstrumentor.instrument()
    RequestsInstrumentor.instrument()
    LoggingInstrumentor.instrument()
    
    return tracer_provider.get_tracer(__name__)

# Create global tracer
tracer = setup_opentelemetry()

class AgentMetrics:
    """Metrics collection for agent orchestration"""
    
    def __init__(self):
        self.tracer = trace.get_tracer(__name__)
    
    def trace_agent_execution(self, agent_name: str, operation: str):
        """Create a span for agent execution"""
        return self.tracer.start_as_current_span(
            f"agent.{agent_name}.{operation}",
            kind=trace.SpanKind.INTERNAL,
            attributes={
                "agent.name": agent_name,
                "agent.operation": operation,
            }
        )
    
    def trace_workflow_execution(self, workflow_id: str, workflow_name: str):
        """Create a span for workflow execution"""
        return self.tracer.start_as_current_span(
            f"workflow.{workflow_name}",
            kind=trace.SpanKind.INTERNAL,
            attributes={
                "workflow.id": workflow_id,
                "workflow.name": workflow_name,
            }
        )
