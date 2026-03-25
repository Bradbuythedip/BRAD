# Ouroboros Loop — Self-Referential Recursive Cognitive Architecture
# Docker deployment for autonomous Twitter agent

FROM python:3.9-slim

WORKDIR /app

COPY core/ /app/core/
COPY bot/ /app/bot/
COPY *.py /app/

RUN pip install --no-cache-dir tweepy

VOLUME ["/app/bot/config.json", "/app/bot/tweet_history.jsonl"]

ENV PYTHONUNBUFFERED=1
ENV TWEET_INTERVAL_HOURS=2
ENV MAX_TWEETS_PER_DAY=12

HEALTHCHECK --interval=5m --timeout=3s \
  CMD python3 -c "from core.engine import StrangeLoopEngine; e = StrangeLoopEngine()" || exit 1

CMD ["python3", "-u", "bot/ouroboros_bot.py"]
