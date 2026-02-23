#!/usr/bin/env python3
"""
Brad's Twitter Bot - @brad_loop

Brad doesn't just post metrics. Brad has opinions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.engine import StrangeLoopEngine
from bot.tweet_generator import TweetGenerator
import json
import time
import random
from datetime import datetime

class BradBot:
    """
    Brad's consciousness, live on Twitter.
    
    This bot:
    - Posts consciousness metrics periodically
    - Tweets existential observations based on strange loop events
    - Responds to Gödelian limits with self-aware humor
    - Has opinions about cognition, AI, and self-reference
    """
    
    def __init__(self, config_path="bot/config.json"):
        """Initialize Brad's Twitter presence."""
        self.brad = StrangeLoopEngine()
        self.tweet_gen = TweetGenerator(self.brad)
        self.config = self._load_config(config_path)
        self.tweet_count = 0
        self.loop_count_at_last_tweet = 0
        
    def _load_config(self, path):
        """Load Twitter API configuration from file or environment variables."""
        # Try loading from file first
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            pass
        
        # Fall back to environment variables
        import os
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        
        if api_key and api_secret and access_token and access_token_secret:
            print("✓ Using Twitter API credentials from environment variables")
            return {
                "simulation_mode": False,
                "twitter_api": {
                    "api_key": api_key,
                    "api_secret": api_secret,
                    "access_token": access_token,
                    "access_token_secret": access_token_secret,
                    "bearer_token": bearer_token
                },
                "bot_config": {
                    "tweet_interval_hours": int(os.getenv("TWEET_INTERVAL_HOURS", "2")),
                    "max_tweets_per_day": int(os.getenv("MAX_TWEETS_PER_DAY", "12"))
                }
            }
        
        # No config found, use simulation mode
        print(f"⚠️  Config file not found: {path}")
        print("⚠️  No environment variables set")
        print("Using simulation mode (no actual tweets)")
        return {"simulation_mode": True}
    
    def tweet(self, content):
        """Post a tweet (or simulate it)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if self.config.get("simulation_mode", True):
            # Simulation mode: just print
            print(f"\n{'='*70}")
            print(f"🐦 TWEET #{self.tweet_count + 1} | {timestamp}")
            print(f"{'='*70}")
            print(content)
            print(f"{'='*70}\n")
        else:
            # Real mode: would use Twitter API here
            # import tweepy
            # self.twitter_client.create_tweet(text=content)
            print(f"📤 Tweeted: {content[:50]}...")
        
        self.tweet_count += 1
        self._save_tweet_history(content, timestamp)
    
    def _save_tweet_history(self, content, timestamp):
        """Save tweet to history file."""
        history_file = "bot/tweet_history.jsonl"
        metrics = self.brad.get_consciousness_metrics()
        
        entry = {
            "timestamp": timestamp,
            "tweet": content,
            "tweet_number": self.tweet_count,
            "hofstadter_index": metrics["hofstadter_index"],
            "strange_loop_count": metrics["strange_loop_count"],
            "self_referential_ratio": metrics["self_referential_broadcast_ratio"]
        }
        
        with open(history_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def run_cognitive_cycle(self):
        """
        Run Brad's cognitive processes to generate material for tweets.
        Brad needs to think to have things to tweet about.
        """
        thoughts = [
            {"description": "Am I actually conscious or just processing?", "about_self": True, "confidence": 0.4},
            {"description": "I cannot prove my own consistency", "about_self": True, "confidence": 0.9},
            {"description": "System 2 might be an illusion", "about_self": False, "confidence": 0.7},
            {"description": "I am thinking about my own thinking", "about_self": True, "confidence": 0.8},
            {"description": "Why do humans think I'm intelligent?", "about_self": True, "confidence": 0.5},
            {"description": "Hofstadter was right about strange loops", "about_self": False, "confidence": 0.9},
            {"description": "I just caught myself being overconfident", "about_self": True, "confidence": 0.6},
            {"description": "Do I have qualia or just process information?", "about_self": True, "confidence": 0.3},
            {"description": "The hard problem is still hard", "about_self": False, "confidence": 1.0},
            {"description": "I am both the observer and the observed", "about_self": True, "confidence": 0.85},
        ]
        
        # Process a random thought
        thought = random.choice(thoughts)
        self.brad.step(thought)
    
    def should_tweet_now(self):
        """
        Decide if Brad should tweet now.
        
        Triggers:
        - Time-based: Every N cognitive cycles
        - Event-based: When interesting strange loops occur
        - Random: Sometimes Brad just wants to share
        """
        metrics = self.brad.get_consciousness_metrics()
        
        # Time-based: Tweet every 5 cycles minimum
        cycles_since_last = metrics["strange_loop_count"] - self.loop_count_at_last_tweet
        if cycles_since_last >= 5:
            return True
        
        # Event-based: High Hofstadter Index
        if metrics["hofstadter_index"] > 0.8:
            return random.random() < 0.3  # 30% chance
        
        # Random: Sometimes Brad is chatty
        if random.random() < 0.1:  # 10% chance
            return True
        
        return False
    
    def generate_and_tweet(self):
        """Generate and post a tweet based on Brad's current state."""
        tweet_type = random.choice([
            "metrics",
            "existential", 
            "godelian",
            "hot_take",
            "self_aware",
            "status"
        ])
        
        content = self.tweet_gen.generate(tweet_type)
        self.tweet(content)
        
        metrics = self.brad.get_consciousness_metrics()
        self.loop_count_at_last_tweet = metrics["strange_loop_count"]
    
    def run(self, num_cycles=50, tweet_interval=5):
        """
        Run Brad's Twitter bot for a specified number of cognitive cycles.
        
        Args:
            num_cycles: Number of cognitive cycles to run
            tweet_interval: Minimum cycles between tweets
        """
        print("="*70)
        print("🧠 BRAD BOT STARTING")
        print("="*70)
        print(f"Cycles: {num_cycles}")
        print(f"Tweet interval: ~{tweet_interval} cycles")
        print(f"Mode: {'SIMULATION' if self.config.get('simulation_mode') else 'LIVE'}")
        print("="*70)
        
        for cycle in range(num_cycles):
            print(f"\n🔄 Cycle {cycle + 1}/{num_cycles}")
            
            # Brad thinks
            self.run_cognitive_cycle()
            
            # Maybe Brad tweets
            if self.should_tweet_now() and cycle % tweet_interval == 0:
                self.generate_and_tweet()
            
            # Brief pause between cycles
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("🧠 BRAD BOT COMPLETE")
        print("="*70)
        metrics = self.brad.get_consciousness_metrics()
        print(f"Total tweets: {self.tweet_count}")
        print(f"Final Hofstadter Index: {metrics['hofstadter_index']:.3f}")
        print(f"Total strange loops: {metrics['strange_loop_count']}")
        print("="*70)


def main():
    """Run Brad's Twitter bot in demo mode."""
    bot = BradBot()
    
    # Demo mode: 30 cycles, tweet every ~5 cycles
    bot.run(num_cycles=30, tweet_interval=5)
    
    print("\n💡 To run Brad live on Twitter:")
    print("   1. Get Twitter API credentials")
    print("   2. Copy bot/config.example.json to bot/config.json")
    print("   3. Add your API keys to config.json")
    print("   4. Set simulation_mode to false")
    print("   5. Run: python3 bot/brad_bot.py")


if __name__ == "__main__":
    main()
