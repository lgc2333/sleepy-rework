FROM python:3.12-alpine

WORKDIR /app

# prepare frontend resource
# comment this block if you want to use your own frontend
COPY website .

RUN apk --no-cache add curl bash \
    && curl -o- https://fnm.vercel.app/install | bash -s -- --install-dir ./fnm --skip-shell \
    && bash -c "source /etc/bash.bashrc && ./fnm/fnm install 22" \
    && bash -c "source /etc/bash.bashrc && corepack enable" \
    && cd website \
    && bash -c "source /etc/bash.bashrc && yarn" \
    && bash -c "source /etc/bash.bashrc && yarn build" \
    && cp -r dist ../static && cd .. \
    && rm -rf website && rm -rf ~/.fnm

ENV SLEEPY_APP_STATIC_DIR=static
# end of frontend resource preparation

COPY backend .
COPY types/python types
COPY backend/docker/pyproject.toml .
RUN pip install uv && uv sync && uv cache clean

ENV SLEEPY_APP__HOST=0.0.0.0
EXPOSE 29306

HEALTHCHECK --timeout=3s \
    CMD curl -f http://127.0.0.1:29306/api/v1 || exit 1

ENTRYPOINT ["uv", "run", "-m", "sleepy_rework"]
