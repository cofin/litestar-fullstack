ARG PYTHON_BUILDER_IMAGE=3.11-slim-bookworm

## ---------------------------------------------------------------------------------- ##
## ------------------------- Python base -------------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
FROM python:${PYTHON_BUILDER_IMAGE} as python-base
ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends git tini \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false\
    && mkdir -p /workspace/app \
    && pip install --quiet -U pip wheel setuptools virtualenv

## ---------------------------------------------------------------------------------- ##
## ------------------------- Python build base -------------------------------------- ##
## ---------------------------------------------------------------------------------- ##
FROM python-base AS build-base
ARG POETRY_INSTALL_ARGS="--only main"
ENV POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_ALWAYS_COPY=1 \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_VERSION='1.5.1' \
    POETRY_INSTALL_ARGS="${POETRY_INSTALL_ARGS}" \
    GRPC_PYTHON_BUILD_WITH_CYTHON=1 \
    PATH="/workspace/app/.venv/bin:/usr/local/bin:$PATH"
## -------------------------- add build packages ----------------------------------- ##
RUN apt-get install -y --no-install-recommends build-essential curl \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /root/.cache \
    && rm -rf /var/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && curl -sSL https://install.python-poetry.org | python - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

## -------------------------- install application ----------------------------------- ##
WORKDIR /workspace/app
COPY pyproject.toml poetry.lock README.md mkdocs.yml mypy.ini .pre-commit-config.yaml .pylintrc LICENSE Makefile \
    package.json package-lock.json vite.config.ts tsconfig.json \
    ./
COPY scripts ./scripts/
RUN python -m venv --copies /workspace/app/.venv \
    && /workspace/app/.venv/bin/pip install --quiet nodeenv cython  \
    && poetry install ${POETRY_INSTALL_ARGS} --no-root --quiet \
    && poetry export ${POETRY_INSTALL_ARGS} --quiet --without-hashes --output=requirements.txt
COPY src ./src/
RUN poetry build --quiet


## ---------------------------------------------------------------------------------- ##
## -------------------------------- runtime build ----------------------------------- ##
## ---------------------------------------------------------------------------------- ##
## ------------------------- use base image  ---------------------------------------- ##

FROM python-base as run-image
ARG ENV_SECRETS="runtime-secrets"
ENV ENV_SECRETS="${ENV_SECRETS}"
RUN addgroup --system --gid 65532 nonroot \
    && adduser --no-create-home --system --uid 65532 nonroot \
    && chown -R nonroot:nonroot /workspace
## -------------------------- install application ----------------------------------- ##
COPY --from=build-base --chown=65532:65532 /workspace/app/requirements.txt /tmp/requirements.txt
COPY --from=build-base --chown=65532:65532 /workspace/app/dist /tmp/
WORKDIR /workspace/app
RUN pip install --quiet --disable-pip-version-check --no-deps --requirement=/tmp/requirements.txt
RUN pip install --quiet --disable-pip-version-check --no-deps /tmp/*.whl
USER nonroot
STOPSIGNAL SIGINT
EXPOSE 8000/tcp
ENTRYPOINT ["tini","--" ]
CMD [ "litestar","run"]
VOLUME /workspace/app