FROM ghcr.io/astral-sh/uv:python3.14-alpine

WORKDIR /app
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --no-dev

# copie les code source
COPY ./main.py .

ENTRYPOINT ["uv", "run", "main.py"]