FROM python:3.12-alpine

WORKDIR /app

# prepare frontend resource
# comment this block if you want to use your own frontend
COPY website /app/website
COPY backend/docker/fnm-setup.sh .

RUN apk --no-cache add curl bash && bash fnm-setup.sh && rm fnm-setup.sh

ENV SLEEPY_APP_STATIC_DIR=static
# end of frontend resource preparation

COPY backend /app/backend
COPY types/python /app/types
COPY backend/docker/pyproject.toml .
RUN pip install uv && uv sync && uv cache clean

ENV SLEEPY_APP__HOST=0.0.0.0
EXPOSE 29306

HEALTHCHECK --timeout=3s \
    CMD curl -f http://127.0.0.1:29306/api/v1 || exit 1

ENTRYPOINT ["uv", "run", "-m", "sleepy_rework"]
