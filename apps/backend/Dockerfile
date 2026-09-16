FROM python:3.14-slim

WORKDIR /backend

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv  \
    uv sync --locked --no-dev

COPY . .

ENV PATH="/backend/.venv/bin:$PATH"

EXPOSE 8000

CMD ["fastapi", "run", "--workers", "5"]
