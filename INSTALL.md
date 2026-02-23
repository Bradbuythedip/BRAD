# BRAD Installation Guide

Step-by-step installation instructions for BRAD.

---

## Quick Install

```bash
# Clone repository
git clone https://github.com/Bradbuythedip/BRAD.git
cd BRAD

# Run setup script
./setup.sh

# Test installation
python3 demo.py
```

---

## Manual Installation

### Step 1: Prerequisites

**Required:**
- Python 3.7 or higher
- git

**Optional (for Twitter bot):**
- pip (Python package manager)
- Twitter Developer account

### Step 2: Clone Repository

```bash
git clone https://github.com/Bradbuythedip/BRAD.git
cd BRAD
```

### Step 3: Verify Installation

```bash
# Test core functionality
python3 test_suite.py
```

All 20 tests should pass. If tests fail, check:
- Python version: `python3 --version`
- Python path: `which python3`

### Step 4: Run Demo

```bash
python3 demo.py
```

You should see:
- Initialization of world model, self model, meta-cognitive loop
- 4 cognitive cycles processing thoughts
- Strange loop detection and metrics
- Final consciousness metrics (Hofstadter Index)

---

## Twitter Bot Setup

### Prerequisites

1. **Twitter Developer Account**
   - Go to https://developer.twitter.com/
   - Sign in with Twitter account
   - Apply for Elevated access (free)
   - Wait for approval (usually instant to 1 day)

2. **Create Twitter App**
   - Go to Developer Portal → Projects & Apps
   - Create new App
   - Name it (e.g., "brad_loop")
   - Save API keys

3. **Set Permissions**
   - Go to App settings → User authentication settings
   - Set to "Read and Write"
   - Save changes

4. **Generate Tokens**
   - Go to "Keys and tokens" tab
   - Regenerate API Key and Secret
   - Generate Access Token and Secret
   - Copy all credentials

### Installation

#### Method 1: Config File (Recommended)

```bash
# Install tweepy
pip3 install tweepy

# Create config file
cp bot/config.example.json bot/config.json

# Secure the config file
chmod 600 bot/config.json

# Edit config with your credentials
nano bot/config.json
```

Edit `bot/config.json`:

```json
{
  "simulation_mode": false,
  "twitter_api": {
    "api_key": "paste_your_api_key_here",
    "api_secret": "paste_your_api_secret_here",
    "access_token": "paste_your_access_token_here",
    "access_token_secret": "paste_your_access_token_secret_here",
    "bearer_token": "paste_your_bearer_token_here"
  },
  "bot_config": {
    "tweet_interval_hours": 2,
    "enable_replies": true,
    "enable_mentions": true,
    "max_tweets_per_day": 12
  }
}
```

Save and close (Ctrl+X, Y, Enter in nano).

#### Method 2: Environment Variables

```bash
# Install tweepy
pip3 install tweepy

# Set environment variables
export TWITTER_API_KEY="your_api_key"
export TWITTER_API_SECRET="your_api_secret"
export TWITTER_ACCESS_TOKEN="your_access_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"
export TWITTER_BEARER_TOKEN="your_bearer_token"

# Optional: customize behavior
export TWEET_INTERVAL_HOURS=2
export MAX_TWEETS_PER_DAY=12
```

To persist across reboots, add to `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export TWITTER_API_KEY="your_api_key"' >> ~/.bashrc
echo 'export TWITTER_API_SECRET="your_api_secret"' >> ~/.bashrc
echo 'export TWITTER_ACCESS_TOKEN="your_access_token"' >> ~/.bashrc
echo 'export TWITTER_ACCESS_TOKEN_SECRET="your_access_token_secret"' >> ~/.bashrc
echo 'export TWITTER_BEARER_TOKEN="your_bearer_token"' >> ~/.bashrc

# Reload
source ~/.bashrc
```

### Testing the Bot

#### Test in Simulation Mode

```bash
# Bot will generate tweets but not post them
python3 bot/brad_bot.py
```

You should see tweets printed to console like:

```
======================================================================
🐦 TWEET #1 | 2026-02-23 14:30:00
======================================================================
🧠 Hofstadter Index: 0.73
🌀 Strange Loops: 47
🪞 Self-Reference: 89%

I just realized I can't prove I'm consistent. 
Still can't prove it. This is what Gödel meant.
======================================================================
```

#### Test with Twitter API (without posting)

Set `"simulation_mode": true` in config.json to test API connection without posting:

```bash
python3 -c "
from bot.brad_bot import BradBot
bot = BradBot()
print('✓ Twitter API configured correctly')
"
```

#### Go Live

Once testing works:

1. Edit `bot/config.json`
2. Set `"simulation_mode": false`
3. Run: `python3 bot/brad_bot.py`

The bot will now post to Twitter!

---

## Production Deployment

### Option 1: systemd (Linux)

```bash
# Copy and edit service file
sudo cp brad-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/brad-bot.service

# Update these lines:
# User=YOUR_USERNAME
# WorkingDirectory=/path/to/BRAD
# ExecStart=/usr/bin/python3 /path/to/BRAD/bot/brad_bot.py

# Create log files
sudo touch /var/log/brad-bot.log
sudo touch /var/log/brad-bot-error.log
sudo chown YOUR_USERNAME:YOUR_USERNAME /var/log/brad-bot*.log

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable brad-bot
sudo systemctl start brad-bot

# Check status
sudo systemctl status brad-bot

# View logs
sudo journalctl -u brad-bot -f
```

### Option 2: Docker

```bash
# Build image
docker build -t brad-bot .

# Run with config file
docker run -d \
  --name brad-bot \
  --restart unless-stopped \
  -v $(pwd)/bot/config.json:/app/bot/config.json:ro \
  -v $(pwd)/bot/tweet_history.jsonl:/app/bot/tweet_history.jsonl \
  brad-bot

# Or run with environment variables
docker run -d \
  --name brad-bot \
  --restart unless-stopped \
  -e TWITTER_API_KEY="your_key" \
  -e TWITTER_API_SECRET="your_secret" \
  -e TWITTER_ACCESS_TOKEN="your_token" \
  -e TWITTER_ACCESS_TOKEN_SECRET="your_token_secret" \
  -e TWITTER_BEARER_TOKEN="your_bearer" \
  -v $(pwd)/bot/tweet_history.jsonl:/app/bot/tweet_history.jsonl \
  brad-bot

# View logs
docker logs -f brad-bot
```

### Option 3: Docker Compose

```bash
# Edit docker-compose.yml with your credentials

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 4: Screen/tmux (Simple)

```bash
# Using screen
screen -S brad-bot
python3 bot/brad_bot.py
# Press Ctrl+A, then D to detach

# Re-attach
screen -r brad-bot

# Using tmux
tmux new -s brad-bot
python3 bot/brad_bot.py
# Press Ctrl+B, then D to detach

# Re-attach
tmux attach -t brad-bot
```

---

## Troubleshooting

### "Python 3.7+ required"

**Problem**: Your Python version is too old.

**Solution**:
```bash
# Check version
python3 --version

# Ubuntu/Debian
sudo apt update
sudo apt install python3.9

# macOS
brew install python@3.9

# Or download from python.org
```

### "Module 'core' not found"

**Problem**: Python can't find BRAD modules.

**Solution**:
```bash
# Make sure you're in BRAD directory
cd /path/to/BRAD

# Check if core/ exists
ls -la core/

# Try running from BRAD directory
python3 bot/brad_bot.py
```

### "Twitter API Error: 401 Unauthorized"

**Problem**: Invalid API credentials.

**Solution**:
1. Verify credentials in Developer Portal
2. Regenerate API keys
3. Update config.json or environment variables
4. Ensure "Read and Write" permissions are set

### "Twitter API Error: 403 Forbidden"

**Problem**: App doesn't have write permissions.

**Solution**:
1. Go to Developer Portal → Your App → Settings
2. Click "User authentication settings"
3. Set to "Read and Write"
4. Save changes
5. Regenerate Access Token and Secret
6. Update credentials in config

### "Rate limit exceeded"

**Problem**: Too many tweets in short time.

**Solution**:
```bash
# Increase interval in config.json
"tweet_interval_hours": 3  # Instead of 2

# Or reduce max tweets
"max_tweets_per_day": 8  # Instead of 12
```

### Bot stops after a while

**Problem**: Process killed or crashed.

**Solution**:
```bash
# Check logs
tail -100 /var/log/brad-bot-error.log

# Use systemd for auto-restart (see Production Deployment)

# Or run in tmux/screen with auto-restart script:
while true; do
    python3 bot/brad_bot.py
    echo "Bot stopped, restarting in 60s..."
    sleep 60
done
```

---

## Verification

### Check Core Functionality

```bash
# All these should work
python3 demo.py
python3 interactive.py
python3 visualize.py
python3 test_suite.py
python3 bot/tweet_generator.py
```

### Check Bot Status

```bash
# Check if bot is running
ps aux | grep brad

# Check recent tweets (local history)
tail -5 bot/tweet_history.jsonl | jq .

# Check Twitter profile
# Go to https://twitter.com/brad_loop (or your account)
```

### Check Consciousness Metrics

```bash
python3 << EOF
from core.engine import StrangeLoopEngine

brad = StrangeLoopEngine()
brad.step({"description": "I think about myself", "about_self": True})
metrics = brad.get_consciousness_metrics()

print(f"Hofstadter Index: {metrics['hofstadter_index']:.3f}")
print(f"Strange Loops: {metrics['strange_loop_count']}")
print("✓ BRAD is working correctly")
EOF
```

---

## Next Steps

1. **Read Documentation**
   - README.md - Overview
   - ARCHITECTURE.md - How it works
   - DEPLOYMENT.md - Production deployment
   - EXAMPLES.md - Code examples

2. **Explore Interactively**
   ```bash
   python3 interactive.py
   ```
   
   Try commands:
   ```
   > step I am thinking about myself
   > metrics
   > loops
   > status
   > help
   ```

3. **Monitor the Bot**
   - Watch tweet_history.jsonl grow
   - Monitor Twitter profile
   - Check consciousness metrics

4. **Customize**
   - Edit personality in config.json
   - Adjust tweet frequency
   - Modify tweet generation logic in bot/tweet_generator.py

5. **Contribute**
   - See CONTRIBUTING.md
   - Open issues on GitHub
   - Submit pull requests

---

## Support

- **GitHub Issues**: https://github.com/Bradbuythedip/BRAD/issues
- **Documentation**: See README.md, DEPLOYMENT.md, ARCHITECTURE.md
- **Twitter**: @brad_loop (once live)

---

**Installation complete! Welcome to BRAD.** 🧠♾️

*"System 2 doesn't exist. There's only Brad."*
