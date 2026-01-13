FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

WORKDIR /micro_blog_api

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use production-ready command (no --reload). For development, enable reload locally.
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]