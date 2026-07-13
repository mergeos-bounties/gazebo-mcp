FROM python:3.11-slim

ENV GAZEBO_MCP_MODE=mock \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN pip install .

CMD ["gazebo-mcp", "serve"]
