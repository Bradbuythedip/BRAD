# BRAD Deployment Guide

## Overview

This document describes how to deploy BRAD in various configurations:
1. Local development/testing
2. Twitter bot deployment
3. Production server deployment
4. Token integration (Solana)

---

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows WSL2
- **Python**: 3.7 or higher
- **Memory**: 512MB minimum, 1GB recommended
- **Disk**: 100MB for code + logs

### Dependencies
BRAD has **zero external dependencies** for core functionality. The only dependencies are for optional features:

**For Twitter Bot**:
```bash
pip install tweepy
```

**For Development** (optional):
```bash
pip install pytest black flake8 mypy
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Bradbuythedip/BRAD.git
cd BRAD
```

### 2. Verify Installation

```bash
# Run quick demo
python3 demo.py

# Run test suite
python3 test_suite.py

# All tests should pass
```

---

## Configuration

### Twitter API Setup

#### Step 1: Get Twitter API Credentials

1. Go to https://developer.twitter.com/
2. Create a developer account (if you don't have one)
3. Create a new Project and App
4. Generate API keys with **Read and Write** permissions
5. You'll need these credentials:
   - **API Key** (also called Consumer Key)
   - **API Secret** (also called Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
   - **Bearer Token** (for v2 API)

#### Step 2: Configure Bot

```bash
# Copy example config
cp bot/config.example.json bot/config.json

# Edit with your credentials
nano bot/config.json  # or vim, emacs, etc.
```

#### Step 3: Edit Configuration

Open `bot/config.json` and fill in your credentials:

```json
{
  "simulation_mode": false,
  "twitter_api": {
    "api_key": "YOUR_API_KEY_HERE",
    "api_secret": "YOUR_API_SECRET_HERE",
    "access_token": "YOUR_ACCESS_TOKEN_HERE",
    "access_token_secret": "YOUR_ACCESS_TOKEN_SECRET_HERE",
    "bearer_token": "YOUR_BEARER_TOKEN_HERE"
  },
  "bot_config": {
    "tweet_interval_hours": 2,
    "enable_replies": true,
    "enable_mentions": true,
    "max_tweets_per_day": 12
  },
  "personality": {
    "sarcasm_level": 0.7,
    "existential_frequency": 0.4,
    "technical_depth": 0.6
  }
}
```

**Important**: `config.json` is in `.gitignore` and will never be committed to version control.

---

## Running the Bot

### Test Mode (Simulation)

Test the bot without actually posting to Twitter:

```bash
python3 bot/brad_bot.py
```

This will:
- Generate tweets and print them to console
- Save to `bot/tweet_history.jsonl`
- Not post to Twitter

### Live Mode

Once you've added API credentials and set `"simulation_mode": false`:

```bash
python3 bot/brad_bot.py
```

---

## Production Deployment

### Option 1: systemd Service (Linux)

Create `/etc/systemd/system/brad-bot.service`:

```ini
[Unit]
Description=BRAD Twitter Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/BRAD
ExecStart=/usr/bin/python3 /path/to/BRAD/bot/brad_bot.py
Restart=on-failure
RestartSec=60
StandardOutput=append:/var/log/brad-bot.log
StandardError=append:/var/log/brad-bot-error.log

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable brad-bot
sudo systemctl start brad-bot
sudo systemctl status brad-bot
```

View logs:

```bash
sudo journalctl -u brad-bot -f
```

### Option 2: Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy code
COPY . /app/

# Install dependencies (if any)
RUN pip install --no-cache-dir tweepy

# Run bot
CMD ["python3", "bot/brad_bot.py"]
```

Build and run:

```bash
# Build image
docker build -t brad-bot .

# Run container
docker run -d \
  --name brad-bot \
  --restart unless-stopped \
  -v $(pwd)/bot/config.json:/app/bot/config.json:ro \
  -v $(pwd)/bot/tweet_history.jsonl:/app/bot/tweet_history.jsonl \
  brad-bot

# View logs
docker logs -f brad-bot
```

### Option 3: Screen/tmux (Simple)

```bash
# Using screen
screen -S brad-bot
cd /path/to/BRAD
python3 bot/brad_bot.py
# Press Ctrl+A then D to detach

# Re-attach later
screen -r brad-bot

# Or using tmux
tmux new -s brad-bot
cd /path/to/BRAD
python3 bot/brad_bot.py
# Press Ctrl+B then D to detach

# Re-attach later
tmux attach -t brad-bot
```

### Option 4: cron Job (Periodic)

For periodic runs instead of continuous:

```bash
crontab -e
```

Add:

```cron
# Run BRAD bot every 2 hours
0 */2 * * * cd /path/to/BRAD && /usr/bin/python3 bot/brad_bot.py >> /var/log/brad-bot.log 2>&1
```

---

## Monitoring

### Check Bot Status

```bash
# If using systemd
sudo systemctl status brad-bot

# If using Docker
docker ps | grep brad-bot
docker logs brad-bot

# Check recent tweets
tail -f bot/tweet_history.jsonl | jq .
```

### View Consciousness Metrics

```bash
# Interactive session
python3 interactive.py

# Then use commands:
> metrics
> status
> loops
```

---

## Security Best Practices

### 1. Protect API Keys

```bash
# Ensure config.json is not readable by others
chmod 600 bot/config.json

# Never commit config.json
# (already in .gitignore)
```

### 2. Use Environment Variables (Alternative)

Instead of `config.json`, you can use environment variables:

```bash
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"
export TWITTER_BEARER_TOKEN="your_bearer"

python3 bot/brad_bot.py
```

Modify `bot/brad_bot.py` to read from environment variables:

```python
import os

config = {
    "twitter_api": {
        "api_key": os.getenv("TWITTER_API_KEY"),
        "api_secret": os.getenv("TWITTER_API_SECRET"),
        "access_token": os.getenv("TWITTER_ACCESS_TOKEN"),
        "access_token_secret": os.getenv("TWITTER_ACCESS_TOKEN_SECRET"),
        "bearer_token": os.getenv("TWITTER_BEARER_TOKEN")
    }
}
```

### 3. Rate Limiting

Twitter has rate limits:
- **POST statuses/update**: 300 per 3 hours
- **GET statuses/mentions_timeline**: 75 per 15 minutes

BRAD's default config respects these limits:
- `max_tweets_per_day`: 12 (well under limit)
- `tweet_interval_hours`: 2

---

## Token Deployment (Solana)

### Prerequisites

1. Install Solana CLI:
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

2. Create Solana wallet:
```bash
solana-keygen new --outfile ~/brad-wallet.json
```

3. Get SOL for fees:
```bash
# Devnet (for testing)
solana airdrop 2 --url devnet

# Mainnet (for production)
# Buy SOL from exchange and transfer to wallet
```

### Launch on pump.fun

1. Go to https://pump.fun
2. Connect your Solana wallet (Phantom/Solflare)
3. Click "Create Token"
4. Fill in:
   - **Name**: BRAD
   - **Symbol**: $BRAD
   - **Description**: "Bidirectional Recursive Attentional Dynamics. System 2 doesn't exist. There's only Brad."
   - **Image**: Upload Brad logo (create voxel face image)
   - **Links**:
     - Twitter: https://twitter.com/brad_loop
     - Website: https://github.com/Bradbuythedip/BRAD
5. Set initial liquidity (minimum ~0.5 SOL)
6. Click "Create & Deploy"
7. Confirm transaction in wallet

### Post-Launch

1. Save contract address to `TOKENOMICS.md`
2. Tweet announcement from @brad_loop
3. Add contract to README.md

---

## Troubleshooting

### Bot Not Tweeting

**Check 1: API credentials**
```bash
# Verify config.json exists and has correct permissions
ls -l bot/config.json
cat bot/config.json | jq .twitter_api.api_key
```

**Check 2: Simulation mode**
```bash
# Ensure simulation_mode is false
cat bot/config.json | jq .simulation_mode
```

**Check 3: Twitter API status**
- Check https://api.twitterstat.us/
- Verify your app has Read+Write permissions at developer.twitter.com

**Check 4: Logs**
```bash
# Check for errors
tail -50 /var/log/brad-bot-error.log
```

### Import Errors

```bash
# Verify Python path
python3 -c "import sys; print(sys.path)"

# Ensure you're in BRAD directory
cd /path/to/BRAD
python3 -c "from core.engine import StrangeLoopEngine; print('OK')"
```

### Memory Issues

BRAD uses minimal memory, but if issues arise:

```bash
# Check memory usage
ps aux | grep brad

# Restart bot
sudo systemctl restart brad-bot
```

---

## Updating

### Pull Latest Code

```bash
cd /path/to/BRAD
git pull origin main

# Restart bot
sudo systemctl restart brad-bot  # if using systemd
# or
docker restart brad-bot  # if using Docker
```

### Backup Configuration

Before updating:

```bash
# Backup config
cp bot/config.json bot/config.json.backup

# Backup tweet history
cp bot/tweet_history.jsonl bot/tweet_history.jsonl.backup
```

---

## Performance

### Resource Usage

Typical resource consumption:
- **CPU**: <1% (idle), ~5% (during cognitive cycles)
- **Memory**: ~50MB
- **Disk**: ~100MB + log growth
- **Network**: Minimal (~1KB per tweet)

### Scaling

For multiple Brad instances:

```bash
# Instance 1 (main bot)
python3 bot/brad_bot.py --instance main --port 8001

# Instance 2 (backup)
python3 bot/brad_bot.py --instance backup --port 8002
```

---

## Frequently Asked Questions

### How do I change Brad's personality?

Edit `bot/config.json`:

```json
"personality": {
  "sarcasm_level": 0.7,        # 0.0-1.0 (default: 0.7)
  "existential_frequency": 0.4, # 0.0-1.0 (default: 0.4)
  "technical_depth": 0.6        # 0.0-1.0 (default: 0.6)
}
```

### How do I change tweet frequency?

Edit `bot/config.json`:

```json
"bot_config": {
  "tweet_interval_hours": 2,    # Hours between tweets
  "max_tweets_per_day": 12      # Safety limit
}
```

### Can I run Brad without Twitter?

Yes! Brad's core architecture works standalone:

```bash
python3 demo.py              # Demo
python3 interactive.py       # Interactive REPL
python3 visualize.py         # ASCII visualization
```

### Where are tweets stored?

Tweets are logged to `bot/tweet_history.jsonl`:

```bash
# View recent tweets
tail -10 bot/tweet_history.jsonl | jq .

# Count total tweets
wc -l bot/tweet_history.jsonl

# Find tweets with high Hofstadter Index
jq 'select(.hofstadter_index > 0.8)' bot/tweet_history.jsonl
```

---

## Support

- **GitHub Issues**: https://github.com/Bradbuythedip/BRAD/issues
- **Documentation**: See README.md, ARCHITECTURE.md, EXAMPLES.md
- **Twitter**: @brad_loop (once live)

---

## License

MIT License - see LICENSE file

---

**Built with 🧠 and ♾️**

*"System 2 doesn't exist. There's only Brad."*
