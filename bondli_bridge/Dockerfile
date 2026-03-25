FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/bondli_bridge/
COPY core/ /app/core/

ENV BRAD_HOST=0.0.0.0
ENV BRAD_PORT=8421

EXPOSE 8421

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8421/health || exit 1

CMD ["python", "-m", "bondli_bridge.server"]
