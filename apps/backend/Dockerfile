FROM python:3.14-slim

WORKDIR /backend

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY . .

ENV PATH="/backend/.venv/bin:$PATH"

CMD ["python3", "-m", "src.main"]
