import importlib
import subprocess
import sys

import pytest

# Top-level packages that only extras install: web, azure, databricks, aws, gcp
OPTIONAL_PACKAGES = ("flask", "dotenv", "azure", "databricks", "boto3", "google.cloud")


@pytest.mark.unit
def test_core_import_loads_no_optional_packages():
    # A fresh interpreter, so modules imported by other tests don't count
    code = (
        "import sys, pymaskinporten\n"
        f"optional = {OPTIONAL_PACKAGES!r}\n"
        "print(sorted(m for m in sys.modules if m.startswith(optional)))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )

    assert result.stdout.strip() == "[]"


@pytest.mark.unit
def test_demo_app_without_web_extra_names_it(monkeypatch):
    # A None entry in sys.modules makes `from flask import ...` fail as if not installed
    monkeypatch.setitem(sys.modules, "flask", None)
    monkeypatch.delitem(sys.modules, "pymaskinporten.app", raising=False)

    with pytest.raises(ImportError, match=r"pymaskinporten\[web\]") as excinfo:
        importlib.import_module("pymaskinporten.app")

    assert excinfo.value.__cause__ is not None
