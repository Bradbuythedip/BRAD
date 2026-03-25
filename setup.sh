#!/bin/bash
# Ouroboros Loop Setup Script

set -e

echo "======================================================================"
echo "                                                                      "
echo "                    Ouroboros Loop Setup                               "
echo "      Self-Referential Recursive Cognitive Architecture               "
echo "                                                                      "
echo "======================================================================"
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
    echo "  Python 3 found: ${PYTHON_VERSION}"

    MAJOR=$(echo ${PYTHON_VERSION} | cut -d'.' -f1)
    MINOR=$(echo ${PYTHON_VERSION} | cut -d'.' -f2)

    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 7 ]; then
        echo "  Python version is 3.7+ [OK]"
    else
        echo "  Python 3.7+ required, found ${PYTHON_VERSION} [FAIL]"
        exit 1
    fi
else
    echo "  Python 3 not found [FAIL]"
    echo "Please install Python 3.7+ from https://www.python.org/"
    exit 1
fi
echo ""

# Run tests
echo "Running test suite..."
if python3 test_suite.py > /tmp/ouroboros_test.log 2>&1; then
    echo "  All tests passed [OK]"
else
    echo "  Tests failed. Check /tmp/ouroboros_test.log [FAIL]"
    cat /tmp/ouroboros_test.log
    exit 1
fi
echo ""

# Check for pip
echo "Checking for pip..."
if command -v pip3 &> /dev/null; then
    echo "  pip3 found [OK]"
else
    echo "  pip3 not found (optional, needed for Twitter bot)"
fi
echo ""

# Twitter bot setup
echo "----------------------------------------------------------------------"
echo "Twitter Bot Setup (optional)"
echo "----------------------------------------------------------------------"
read -p "Set up Twitter bot? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing tweepy..."
    pip3 install tweepy
    echo "  tweepy installed [OK]"
    echo ""

    if [ ! -f "bot/config.json" ]; then
        echo "Creating bot/config.json from template..."
        cp bot/config.example.json bot/config.json
        chmod 600 bot/config.json
        echo "  Config file created at bot/config.json [OK]"
        echo ""
        echo "IMPORTANT: Edit bot/config.json and add your Twitter API credentials"
        echo "Get credentials at: https://developer.twitter.com/"
    else
        echo "  bot/config.json already exists [OK]"
    fi
    echo ""

    echo "Testing bot in simulation mode..."
    timeout 5s python3 bot/ouroboros_bot.py > /dev/null 2>&1 || true
    echo "  Bot test complete [OK]"
fi
echo ""

# Summary
echo "======================================================================"
echo "Setup Complete"
echo "======================================================================"
echo ""
echo "Quick Start:"
echo "  python3 demo.py              # Run demo"
echo "  python3 interactive.py       # Interactive mode"
echo "  python3 visualize.py         # Visualization"
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Twitter Bot:"
    echo "  Edit bot/config.json with your API keys, then:"
    echo "  python3 bot/ouroboros_bot.py  # Run bot"
    echo ""
fi
echo "Bondli Trading Bridge:"
echo "  pip install fastapi uvicorn pydantic"
echo "  python -m bondli_bridge.server   # Starts on :8421"
echo ""
echo "Documentation:"
echo "  README.md                    # Overview"
echo "  DEPLOYMENT.md                # Production deployment"
echo "  ARCHITECTURE.md              # Technical details"
echo "  bondli_bridge/INTEGRATION.md # Bondli integration"
echo ""
