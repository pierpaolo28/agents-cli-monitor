FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/
COPY run_monitoring_sweep.py ./

# Install dependencies
RUN uv sync --frozen

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GOOGLE_GENAI_USE_VERTEXAI=True
ENV TRACKING_FILE_PATH=gs://agents-cli-monitor-${GOOGLE_CLOUD_PROJECT}/agents_cli_mentions.md

# Run the monitoring sweep
CMD ["uv", "run", "python", "run_monitoring_sweep.py"]
