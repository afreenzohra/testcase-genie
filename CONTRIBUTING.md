# 🤝 Contributing to TestCase-Genie

We welcome contributions from the testing, automation, and AI communities! Whether you want to improve prompt designs, add support for more frameworks (like Cypress or Robot Framework), or improve test case parsing, here is how to get started.

---

## 🛠️ Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/afreenzohra/testcase-genie.git
   cd testcase-genie
   ```

2. **Set up a virtual environment (Python 3.11+ recommended):**
   ```bash
   python -m venv venv
   # On Linux/macOS:
   source venv/bin/activate
   # On Windows:
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment:**
   ```bash
   cp .env.example .env
   # Add your Google Gemini API Key in .env
   ```

---

## 🧪 Running Tests

Ensure all unit tests pass before submitting changes:
```bash
# Set PYTHONPATH and run pytest
python -m pytest -v tests/
```

---

## 📐 Coding & Pull Request Standards

1. **Type hints & Docstrings**: All public methods and classes must have complete type hints and descriptive docstrings.
2. **Commit Convention**: We follow Conventional Commits:
   - `feat:` New features or functionality
   - `fix:` Bug fixes
   - `test:` Adding or updating tests
   - `docs:` Documentation improvements
   - `ci:` CI/CD pipeline changes
   - `refactor:` Code refactoring without behavior change
3. **No Hardcoded Secrets**: Never commit `.env` or any API key. Keep all credentials strictly local.
4. **Pull Requests**: Open a pull request against `main` describing your changes and linking relevant issues.
