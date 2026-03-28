FROM python:3.11-slim

WORKDIR /app

COPY bondli_bridge/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY core/ /app/core/
COPY bondli_bridge/ /app/bondli_bridge/

ENV BRAIN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Railway injects PORT at runtime — config.py reads it
EXPOSE ${PORT:-8421}

CMD ["python", "-m", "bondli_bridge"]
