FROM python:3.12-slim

# Set environment variables to prevent generating .pyc files and to run Python in unbuffered mode.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ../../backend backend
COPY ../../types/python types
COPY pyproject.toml .

RUN pip install uv && uv sync

ENV SLEEPY_APP__HOST=0.0.0.0
EXPOSE 29306
CMD ["uv", "run", "-m", "sleepy_rework"]
