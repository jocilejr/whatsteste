# Here are your Instructions

## Environment Variables

### `BAILEYS_URL`

The Baileys integration no longer relies on hard-coded URLs. All modules now read the
Baileys service location from the `BAILEYS_URL` environment variable. If not provided,
`http://localhost:3002` is used by default.

Example usage:

```bash
export BAILEYS_URL=http://baileys.internal:3002
python whatsflow-real.py
```

For the Node.js service:

```bash
BAILEYS_URL=http://baileys.internal:3002 node baileys_service/server.js
```
