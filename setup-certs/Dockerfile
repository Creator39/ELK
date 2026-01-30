FROM ghcr.io/astral-sh/uv:python3.14-alpine

# copie et installe les dépendances
WORKDIR /app
RUN mkdir utils
COPY pyproject.toml .
RUN uv sync --no-dev
RUN apk add --no-cache openssl

# copie les code source
COPY ./certs_config.yaml .
COPY ./utils utils/
COPY ./generate_certs.py .
COPY ./main.py .

ENTRYPOINT ["uv", "run", "main.py"]