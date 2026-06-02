# Tool Risk Levels

| Class | Meaning | Default Policy |
|---|---|---|
| `R0` | Local read-only inspection. | allow |
| `R1` | Local write inside approved workspace. | ask |
| `R2` | External read or API fetch. | ask |
| `R3` | External write or messaging. | ask with explicit destination |
| `R4` | Destructive, admin, secrets, billing, or production data. | deny unless approved per task |

Every tool and MCP server must be assigned a risk class before use.

