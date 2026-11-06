FROM python:3.14-slim

WORKDIR /backend

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN if [ "$ENVIRONMENT" = "production" ]; then \
    --mount=type=cache,target=/root/.cache/uv  \
    uv sync --locked --no-dev; \
    else \
    uv sync --locked --no-dev --no-cache; \
    fi

COPY . .

ENV PATH="/backend/.venv/bin:$PATH"

EXPOSE 80

CMD ["python3", "-m", "src.main"]
