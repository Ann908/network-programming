# CI for Flask API products

Application use Flask and SQLite. `/health` checks server availability. `/items` use HTTP Basic Auth.

## Local tests in PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:PRODUCTS_DATABASE_URI = "sqlite:///:memory:"
.\.venv\Scripts\python.exe -m pytest --cov
.\.venv\Scripts\python.exe -m coverage report --fail-under=90
Remove-Item Env:PRODUCTS_DATABASE_URI
```

## GitHub Actions

Job `test` launch pytest, checks the coverage threshold 90% and keeps
reports `coverage.xml` and `junit.xml`. Job `docker` builds the image after a successful check and publishes it to GHCR upon a push to the `master`
or push tag `v*`.