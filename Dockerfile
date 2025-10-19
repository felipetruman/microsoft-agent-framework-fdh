FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    nodejs \
    npm \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional tools for monitoring and debugging
RUN pip install jupyterlab ipywidgets

# Set up working directory
WORKDIR /workspace

# Copy application code
COPY . .

# Install the application in development mode
RUN pip install -e .

# Create non-root user
RUN useradd -m -u 1000 vscode && \
    chown -R vscode:vscode /workspace
USER vscode

# Expose ports
EXPOSE 8000 8501 7860 3000 8080

# Set environment variables
ENV PYTHONPATH=/workspace
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "streamlit", "run", "src/ui/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
