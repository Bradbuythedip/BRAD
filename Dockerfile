# BRAD - Bidirectional Recursive Attentional Dynamics
# Docker deployment for Twitter bot

FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy source code
COPY core/ /app/core/
COPY bot/ /app/bot/
COPY *.py /app/

# Install dependencies (only for Twitter bot)
RUN pip install --no-cache-dir tweepy

# Create volume mount points
VOLUME ["/app/bot/config.json", "/app/bot/tweet_history.jsonl"]

# Set environment variables (can be overridden)
ENV PYTHONUNBUFFERED=1
ENV TWEET_INTERVAL_HOURS=2
ENV MAX_TWEETS_PER_DAY=12

# Health check
HEALTHCHECK --interval=5m --timeout=3s \
  CMD python3 -c "from core.engine import StrangeLoopEngine; e = StrangeLoopEngine()" || exit 1

# Run bot
CMD ["python3", "-u", "bot/brad_bot.py"]
