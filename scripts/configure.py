import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / ".env"
if path.exists():
    print("Existing .env preserved")
else:
    password = secrets.token_hex(24)
    contents = (
        (root / ".env.example")
        .read_text()
        .replace("POSTGRES_PASSWORD=\n", "POSTGRES_PASSWORD=" + password + "\n")
        .replace("CHANGE_ME", password)
    )
    path.write_text(contents)
    path.chmod(0o600)
    print("Created local .env with a random development database password; no credentials printed")
