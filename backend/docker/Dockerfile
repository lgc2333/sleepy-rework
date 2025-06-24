FROM python:3.12-alpine

WORKDIR /app

COPY backend /app/backend
COPY types/python /app/types
COPY backend/docker/pyproject.toml .
COPY website/dist /app/static
RUN pip install uv && uv sync && uv cache clean

ENV SLEEPY_APP__HOST=0.0.0.0
ENV SLEEPY_APP_STATIC_DIR=static
EXPOSE 29306

HEALTHCHECK --timeout=3s \
    CMD curl -f http://127.0.0.1:29306/api/v1 || exit 1

ENTRYPOINT ["uv", "run", "-m", "sleepy_rework"]
