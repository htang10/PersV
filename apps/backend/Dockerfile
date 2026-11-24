FROM python:3.15-trixie

WORKDIR /backend

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-cache

COPY . .

ENV PATH="/backend/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python3", "-m", "src.main"]
