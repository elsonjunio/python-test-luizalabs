FROM python:3.12-slim AS base


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true


COPY pyproject.toml poetry.lock ./


RUN poetry install --no-interaction --no-ansi --without dev


COPY app ./app
COPY migrations ./migrations
COPY alembic.ini .

EXPOSE 8000

CMD poetry run alembic upgrade head && \
    poetry run fastapi run app/main.py --port 8000 --host 0.0.0.0

#CMD [ "tail", "-f", "/dev/null" ]
