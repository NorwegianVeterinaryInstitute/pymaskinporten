# smoke_test.py

import sys

try:
    from pymaskinporten import main

    assert main() == "Hello from pymaskinporten!"
    print("Smoke test passed: App imported successfully!")
except ImportError as e:
    print(f"Smoke test failed: {e}")
    sys.exit(1)
