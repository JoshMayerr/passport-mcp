I'll outline the steps for testing, building, and publishing BrowserPassport to PyPI.

1. First, let's add a basic test structure to our Python SDK:

2. Update `pyproject.toml` to include test dependencies:

3. Development and Testing Steps:

```bash
# From sdks/python directory

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package in editable mode with test dependencies
pip install -e ".[test]"

# Run tests
pytest tests/
```

4. Build and Publish Steps:

```bash
# Build the package
python -m build

# This will create:
# - dist/browserpassport-0.1.0.tar.gz (source distribution)
# - dist/browserpassport-0.1.0-py3-none-any.whl (wheel)

# Test the build (optional)
pip install dist/browserpassport-0.1.0-py3-none-any.whl

# Publish to TestPyPI first (recommended)
python -m twine upload --repository testpypi dist/*

# Once tested, publish to PyPI
python -m twine upload dist/*
```

5. Required PyPI Setup:

- Create accounts on PyPI (https://pypi.org) and TestPyPI (https://test.pypi.org)
- Create API tokens for authentication
- Create `~/.pypirc` file:

6. GitHub Actions (Optional):
   We can also set up automated testing and publishing. Would you like me to provide a GitHub Actions workflow for this?

Key points to remember:

1. Always test thoroughly before publishing
2. Use TestPyPI first to verify the package
3. Make sure the version number is updated in `pyproject.toml` before building
4. Keep PyPI tokens secure and never commit them to the repository
5. The build process will include the native host files from the shared directory

Let me know if you'd like me to elaborate on any of these steps or provide additional configurations!
