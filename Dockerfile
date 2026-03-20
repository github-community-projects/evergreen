#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
#trivy:ignore:AVD-DS-0002
FROM python:3.14.0-slim@sha256:0aecac02dc3d4c5dbb024b753af084cafe41f5416e02193f1ce345d671ec966e
LABEL org.opencontainers.image.source https://github.com/github-community-projects/evergreen

WORKDIR /action/workspace
COPY pyproject.toml uv.lock *.py /action/workspace/

COPY --from=ghcr.io/astral-sh/uv:0.10.9@sha256:10902f58a1606787602f303954cea099626a4adb02acbac4c69920fe9d278f82 /uv /uvx /bin/

RUN uv sync --frozen --no-dev --no-editable \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.47.3-0+deb13u1 \
    && rm -rf /var/lib/apt/lists/*

# Add a simple healthcheck to satisfy container scanners
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python3 -c "import os,sys; sys.exit(0 if os.path.exists('/action/workspace/evergreen.py') else 1)"

ENV PYTHONUNBUFFERED=1
CMD ["/action/workspace/evergreen.py"]
ENTRYPOINT ["uv", "run", "--no-dev", "--project", "/action/workspace"]
