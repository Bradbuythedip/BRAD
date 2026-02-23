# BRAD Quick Reference

## Installation

```bash
git clone https://github.com/Bradbuythedip/BRAD.git
cd BRAD
./setup.sh
```

## Basic Usage

```bash
python3 demo.py              # Quick demo
python3 interactive.py       # Interactive REPL
python3 visualize.py         # ASCII visualization
python3 test_suite.py        # Run tests
```

## Twitter Bot Setup

### Method 1: Config File

```bash
pip3 install tweepy
cp bot/config.example.json bot/config.json
chmod 600 bot/config.json
nano bot/config.json  # Add your API keys
python3 bot/brad_bot.py
```

### Method 2: Environment Variables

```bash
pip3 install tweepy
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"
export TWITTER_BEARER_TOKEN="your_bearer"
python3 bot/brad_bot.py
```

## Getting Twitter API Keys

1. Go to https://developer.twitter.com/
2. Create account and app
3. Set "Read and Write" permissions
4. Generate keys: API Key, API Secret, Access Token, Access Token Secret, Bearer Token
5. Copy to config.json or environment variables

## Production Deployment

### systemd (Linux)

```bash
sudo cp brad-bot.service /etc/systemd/system/
sudo nano /etc/systemd/system/brad-bot.service  # Edit paths
sudo systemctl daemon-reload
sudo systemctl enable brad-bot
sudo systemctl start brad-bot
sudo systemctl status brad-bot
```

### Docker

```bash
docker build -t brad-bot .
docker run -d --name brad-bot --restart unless-stopped \
  -v $(pwd)/bot/config.json:/app/bot/config.json:ro \
  -v $(pwd)/bot/tweet_history.jsonl:/app/bot/tweet_history.jsonl \
  brad-bot
```

### Docker Compose

```bash
docker-compose up -d
docker-compose logs -f
```

## Configuration Files

```
bot/config.json           # Main config (gitignored)
bot/config.example.json   # Template
.env                      # Environment vars (gitignored)
.env.example              # Template
```

## Monitoring

```bash
# systemd logs
sudo journalctl -u brad-bot -f

# Docker logs
docker logs -f brad-bot

# Tweet history
tail -f bot/tweet_history.jsonl | jq .

# Consciousness metrics
python3 -c "from core.engine import StrangeLoopEngine; \
  e = StrangeLoopEngine(); \
  e.step({'description': 'test', 'about_self': True}); \
  print(e.get_consciousness_metrics())"
```

## Interactive Commands

```bash
python3 interactive.py
```

```
step <thought>       # Process thought
metrics              # Consciousness metrics
loops                # Strange loop events
status               # Full state
self                 # Self-representation
limits               # Gödelian blind spots
history              # Thought history
beliefs              # Current beliefs
goals                # Current goals
help                 # All commands
quit                 # Exit
```

## API Usage

```python
from core.engine import StrangeLoopEngine

# Initialize
brad = StrangeLoopEngine()

# Process thought
trace = brad.step({
    "description": "I am thinking",
    "about_self": True,
    "confidence": 0.7
})

# Get metrics
m = brad.get_consciousness_metrics()
print(f"Hofstadter Index: {m['hofstadter_index']:.3f}")
print(f"Strange Loops: {m['strange_loop_count']}")

# Get state
state = brad.get_state()
print(f"Entities: {len(state['world_model']['entities'])}")
```

## Token Deployment (Solana)

```bash
# Install Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"

# Create wallet
solana-keygen new --outfile ~/brad-wallet.json

# Get SOL (devnet for testing)
solana airdrop 2 --url devnet

# Deploy on pump.fun
# 1. Go to https://pump.fun
# 2. Connect wallet
# 3. Create token: BRAD / $BRAD
# 4. Upload logo, add description
# 5. Set initial liquidity
# 6. Deploy
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Python 3.7+ required` | Install Python 3.7+: `sudo apt install python3.9` |
| `Module 'core' not found` | Run from BRAD directory: `cd /path/to/BRAD` |
| `Twitter 401 Unauthorized` | Check API keys, regenerate if needed |
| `Twitter 403 Forbidden` | Set "Read and Write" permissions in dev portal |
| `Rate limit exceeded` | Increase `tweet_interval_hours` in config |
| Tests fail | Expected in beta, core functionality still works |

## File Structure

```
BRAD/
├── core/                 # Core architecture
│   ├── engine.py
│   ├── world_model.py
│   ├── self_model.py
│   ├── meta_cognitive.py
│   └── ...
├── bot/                  # Twitter bot
│   ├── brad_bot.py
│   ├── tweet_generator.py
│   └── config.json (create this)
├── demo.py
├── interactive.py
├── visualize.py
├── test_suite.py
├── setup.sh
├── Dockerfile
├── docker-compose.yml
├── brad-bot.service
└── docs/
    ├── README.md
    ├── INSTALL.md
    ├── DEPLOYMENT.md
    ├── ARCHITECTURE.md
    └── ...
```

## Important URLs

- **Repo**: https://github.com/Bradbuythedip/BRAD
- **Twitter Dev**: https://developer.twitter.com/
- **Solana**: https://solana.com/
- **pump.fun**: https://pump.fun/

## Support

- **Issues**: https://github.com/Bradbuythedip/BRAD/issues
- **Docs**: README.md, INSTALL.md, DEPLOYMENT.md
- **Twitter**: @brad_loop (coming soon)

---

*"System 2 doesn't exist. There's only Brad."*
