# Security gates

## `path_safety_gate.py`
- **Blocked paths:** `.env`, `.env.production`, `.env.local`, `secrets/`, `infra/prod/`, `db/prod/`, `credentials/`, `private_keys/`.
- **On match:** refuse write; surface to human (severity=critical).
