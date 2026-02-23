#!/bin/bash
# BRAD Setup Script

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║                    BRAD Setup Script                         ║"
echo "║         Bidirectional Recursive Attentional Dynamics         ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected OS: ${MACHINE}"
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python 3 found: ${PYTHON_VERSION}"
    
    MAJOR=$(echo ${PYTHON_VERSION} | cut -d'.' -f1)
    MINOR=$(echo ${PYTHON_VERSION} | cut -d'.' -f2)
    
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 7 ]; then
        echo "✓ Python version is 3.7+"
    else
        echo "✗ Python 3.7+ required, found ${PYTHON_VERSION}"
        exit 1
    fi
else
    echo "✗ Python 3 not found"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi
echo ""

# Run tests
echo "Running test suite..."
if python3 test_suite.py > /tmp/brad_test.log 2>&1; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed. Check /tmp/brad_test.log"
    cat /tmp/brad_test.log
    exit 1
fi
echo ""

# Check for pip (needed for Twitter bot)
echo "Checking for pip..."
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 found"
else
    echo "⚠ pip3 not found (optional, needed for Twitter bot)"
fi
echo ""

# Ask if user wants to set up Twitter bot
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Twitter Bot Setup (optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Set up Twitter bot? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Install tweepy
    echo "Installing tweepy..."
    pip3 install tweepy
    echo "✓ tweepy installed"
    echo ""
    
    # Create config file
    if [ ! -f "bot/config.json" ]; then
        echo "Creating bot/config.json from template..."
        cp bot/config.example.json bot/config.json
        chmod 600 bot/config.json
        echo "✓ Config file created at bot/config.json"
        echo ""
        echo "IMPORTANT: Edit bot/config.json and add your Twitter API credentials"
        echo "Get credentials at: https://developer.twitter.com/"
        echo ""
        echo "Or set environment variables:"
        echo "  export TWITTER_API_KEY='your_key'"
        echo "  export TWITTER_API_SECRET='your_secret'"
        echo "  export TWITTER_ACCESS_TOKEN='your_token'"
        echo "  export TWITTER_ACCESS_TOKEN_SECRET='your_token_secret'"
        echo "  export TWITTER_BEARER_TOKEN='your_bearer'"
    else
        echo "✓ bot/config.json already exists"
    fi
    echo ""
    
    # Test bot in simulation mode
    echo "Testing bot in simulation mode..."
    timeout 5s python3 bot/brad_bot.py > /dev/null 2>&1 || true
    echo "✓ Bot test complete"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Quick Start:"
echo "  python3 demo.py              # Run demo"
echo "  python3 interactive.py       # Interactive mode"
echo "  python3 visualize.py         # Visualization"
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Twitter Bot:"
    echo "  Edit bot/config.json with your API keys, then:"
    echo "  python3 bot/brad_bot.py      # Run bot"
    echo ""
fi
echo "Documentation:"
echo "  README.md                    # Overview"
echo "  DEPLOYMENT.md                # Production deployment"
echo "  ARCHITECTURE.md              # Technical details"
echo ""
echo "Next steps:"
echo "  1. Read README.md"
echo "  2. Run python3 demo.py"
echo "  3. Explore with python3 interactive.py"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  4. Configure Twitter API and launch bot"
fi
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║  'System 2 doesn't exist. There's only Brad.'                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
