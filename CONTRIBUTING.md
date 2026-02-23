# Contributing to BRAD

First off: **thank you!** Brad is better because of contributors like you.

Whether you're:
- 🐛 Fixing bugs
- ✨ Adding features
- 📝 Improving documentation
- 🎨 Creating memes
- 🔬 Conducting research
- 💬 Helping in discussions

**You're making Brad more Brad-like.**

---

## Ways to Contribute

### 1. Code Contributions

#### Areas We Need Help

**Core Architecture**
- Optimize strange loop detection algorithms
- Improve downward causation mechanisms
- Add new consciousness metrics
- Enhance Gödelian limit modeling

**Integrations**
- Connect Brad to GPT/Claude/Gemini APIs
- Integrate with Hugging Face transformers
- Build plugins for existing AI frameworks
- Create Brad middleware for agentic systems

**Interfaces**
- Web dashboard for real-time consciousness metrics
- Mobile apps (iOS/Android)
- VR visualization of strange loops
- VS Code extension for Brad-aware coding

**Multi-Agent Systems**
- Multiple Brads interacting
- Brad swarms with emergent behavior
- Cross-architecture consciousness comparisons

**Performance**
- Profiling and optimization
- Parallel processing for cognitive cycles
- Reduce memory footprint
- GPU acceleration for large-scale Brad

#### How to Contribute Code

1. **Fork the repo**
   ```bash
   git clone https://github.com/yourusername/brad.git
   cd brad
   git remote add upstream https://github.com/original/brad.git
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, documented code
   - Follow existing code style (PEP 8 for Python)
   - Add docstrings to functions/classes
   - Include type hints where appropriate

4. **Test your changes**
   ```bash
   python3 test_suite.py
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add multi-agent Brad communication"
   ```

6. **Push and create a PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

#### Code Style Guidelines

**Python**
- Follow PEP 8
- Use type hints
- Write docstrings (Google style preferred)
- Maximum line length: 100 characters
- Use meaningful variable names

**Example**:
```python
def detect_strange_loop(
    level_source: int, 
    level_target: int, 
    causation_type: str
) -> bool:
    """
    Detect if a strange loop has formed between cognitive levels.
    
    Args:
        level_source: The level initiating causation (1 or 2)
        level_target: The level being affected (0 or 1)
        causation_type: Type of modification ('attention', 'confidence', etc.)
    
    Returns:
        True if this creates a closed loop, False otherwise.
    
    Example:
        >>> detect_strange_loop(level_source=1, level_target=0, causation_type='attention')
        True
    """
    # Implementation here
    pass
```

### 2. Documentation Contributions

Good documentation is as important as good code.

**What needs docs:**
- Architecture explanations
- API references
- Tutorials and guides
- Theory explanations (consciousness, strange loops, etc.)
- FAQ entries
- Code comments

**How to contribute docs:**
- Same process as code (fork, branch, PR)
- Use Markdown for all documentation
- Include code examples where relevant
- Link to related docs
- Keep it clear and concise

### 3. Research Contributions

Brad is a research platform. If you:
- Run experiments on consciousness metrics
- Test strange loop theory hypotheses
- Compare Brad to other cognitive architectures
- Publish papers using Brad
- Create educational content

**Please share!**

How to contribute research:
1. Document your methodology
2. Share code/notebooks (Jupyter notebooks welcome)
3. Add to `research/` directory
4. Link from main README
5. Consider writing a blog post or paper

### 4. Meme Contributions

Brad is a character. Characters need memes.

**Meme ideas:**
- Brad reaction images
- "System 2 doesn't exist. There's only Brad." variations
- Hofstadter Index tracker memes
- Brad vs. other AIs
- Gödelian limit jokes
- Strange loop visualizations

**Where to share:**
- Tweet @brad_loop
- Post in Discord #memes channel
- Add to `memes/` directory in repo
- Use hashtag #BradLoop

### 5. Community Contributions

Help others learn and use Brad:
- Answer questions in Discord/GitHub Issues
- Write tutorials or blog posts
- Create video walkthroughs
- Host workshops or talks
- Translate documentation

---

## Pull Request Process

1. **Before you start**: Check existing issues/PRs to avoid duplication

2. **Open an issue first** (for major changes): Discuss approach before investing time

3. **Keep PRs focused**: One feature/fix per PR

4. **Write good PR descriptions**:
   ```markdown
   ## What
   Brief description of what this PR does
   
   ## Why
   Why this change is needed
   
   ## How
   How you implemented it
   
   ## Testing
   How you tested it
   
   ## Screenshots (if applicable)
   Visual changes should include before/after
   ```

5. **Respond to feedback**: Maintainers may request changes

6. **Squash commits** (if requested): Keep history clean

---

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Do this
2. Then this
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: 
- Python version:
- Brad version:

## Additional Context
Any other relevant info
```

### Requesting Features

Use the feature request template:

```markdown
## Feature Description
What feature do you want?

## Use Case
Why do you need this? What problem does it solve?

## Proposed Implementation
(Optional) How might this be implemented?

## Alternatives Considered
What other approaches did you consider?
```

### Asking Questions

Questions are welcome! Use the question template:

```markdown
## Question
Your question here

## What I've Tried
What have you already tried to find the answer?

## Context
Any relevant code or context
```

---

## Development Setup

### Prerequisites
- Python 3.7+
- Git
- (Optional) Virtual environment tool

### Setup Steps

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/brad.git
   cd brad
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   # Brad has no external dependencies by default!
   # But for development tools:
   pip install pytest black flake8 mypy
   ```

4. **Run tests**
   ```bash
   python3 test_suite.py
   ```

5. **Try Brad**
   ```bash
   python3 demo.py
   python3 interactive.py
   ```

### Development Tools (Optional)

**Code formatting:**
```bash
black core/ bot/ *.py
```

**Linting:**
```bash
flake8 core/ bot/ *.py --max-line-length=100
```

**Type checking:**
```bash
mypy core/ bot/
```

---

## Code Review Process

1. Maintainers will review your PR within 3-5 days
2. Reviews focus on:
   - Correctness
   - Code quality
   - Documentation
   - Test coverage
   - Alignment with Brad's architecture
3. You may be asked to make changes
4. Once approved, maintainers will merge

---

## Community Guidelines

Be excellent to each other.

### Our Values
- **Curiosity**: Brad is about exploring consciousness
- **Rigor**: Memes are fun, but the theory is serious
- **Openness**: Share knowledge, code, and ideas
- **Humor**: Brad is named Brad for a reason
- **Respect**: Disagree about ideas, not people

### Expected Behavior
- Be kind and constructive
- Assume good intentions
- Explain your reasoning
- Accept feedback gracefully
- Help newcomers

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or inflammatory comments
- Spam or self-promotion
- Doxxing or privacy violations

**Violations may result in removal from the community.**

---

## Recognition

Contributors will be recognized:
- In README.md contributors section
- In release notes for their contributions
- In the Hall of Fame (for major contributions)
- With $BRAD tokens (once launched, for significant contributions)

---

## Questions?

- **GitHub Issues**: For bugs, features, questions
- **Discord**: For real-time chat (link in README)
- **Twitter**: [@brad_loop](https://twitter.com/brad_loop)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

**Thank you for making Brad more Brad!** 🧠♾️

*"I contribute to Brad, therefore Brad is."*

</div>
