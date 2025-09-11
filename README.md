# WhatsFlow

This project provides a WhatsApp automation platform with a React frontend and Python backend.

## Groups Tab

The **Grupos** tab contains a single **Criar campanha** button. After naming a campaign, a card appears listing **Selecionar grupos** and **Programar mensagens** options for that campaign.

## Installation

Use the provided `install-whatsflow.sh` script to set up all services:

```bash
chmod +x install-whatsflow.sh
./install-whatsflow.sh
```

The script installs dependencies for the backend, frontend and WhatsApp service and creates a `start-whatsflow.sh` helper.
To start the system after installation run:

```bash
./start-whatsflow.sh
```

## Environment Variables

### `BAILEYS_URL`

The Baileys integration reads the WhatsApp service location from the `BAILEYS_URL` environment variable. If not provided, `http://localhost:3002` is used by default.

Example usage:

```bash
export BAILEYS_URL=http://baileys.internal:3002
python whatsflow-real.py
```

For the Node.js service:

```bash
BAILEYS_URL=http://baileys.internal:3002 node baileys_service/server.js
```
