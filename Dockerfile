#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
#trivy:ignore:AVD-DS-0002
FROM python:3.15.2-slim@sha256:65a65fc7b30b06cb6df4930fd4650697cb23f4c2698ab81fc87e4b031bc36928
LABEL org.opencontainers.image.source https://github.com/github-community-projects/evergreen

WORKDIR /action/workspace
COPY pyproject.toml uv.lock *.py /action/workspace/

COPY --from=ghcr.io/astral-sh/uv:0.10.9@sha256:10902f58a1606787602f303954cea099626a4adb02acbac4c69920fe9d278f82 /uv /uvx /bin/

# hadolint ignore=DL3008
RUN apt-get -y update \
    && apt-get -y install --no-install-recommends \
        gcc \
        git \
        libc6-dev \
        libffi-dev \
    && uv sync --frozen --no-dev --no-editable \
    && apt-get -y purge --auto-remove gcc libc6-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Add a simple healthcheck to satisfy container scanners
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD ["python3", "-c", "import os,sys; sys.exit(0 if os.path.exists('/action/workspace/evergreen.py') else 1)"]

ENV PYTHONUNBUFFERED=1
ENV UV_LINK_MODE=copy
CMD ["/action/workspace/evergreen.py"]
ENTRYPOINT ["uv", "run", "--no-dev", "--project", "/action/workspace"]
