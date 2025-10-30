<div align="center">

# Monero Wallet RPC Web Interface

<img src="static/cuzdan.png" alt="Cuzdan Logo" width="200"/>

A Flask-based web interface for managing Monero wallets with multi-address support, transaction history, XMR sending capabilities, QR code generation and QR code scanning.

</div>

---

## Quick Start
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your wallet settings

# Start Monero wallet RPC (see below)

# Run the application
python app.py
```

Access the wallet at: http://localhost:5000

---

## Starting the Wallet RPC Server

Use the following command to start the RPC server (replace the wallet-file location with your actual path):

```bash
./monero-wallet-rpc \
--rpc-bind-port 18082 \
--daemon-host xmr.surveillance.monster:443 \
--wallet-file /root/Downloads/monero-x86_64-linux-gnu-v0.18.4.3/cuzdan-wallet \
--prompt-for-password \
--trusted-daemon \
--daemon-ssl-allow-any-cert \
--log-file logs/monero-wallet-rpc.log \
--log-level 1 \
--disable-rpc-login
```

**Finding Alternative Nodes:**
If you need to use a different Monero node, you can find a list of available nodes at: https://xmr.ditatompel.com/

Simply replace the `--daemon-host` parameter with your chosen node address.

---

## Configuration

All configuration is done through the `.env` file:
```env
# Monero Wallet Configuration
WALLET_HOST=localhost
WALLET_PORT=18082
WALLET_PASSWORD=your_password

# Flask Configuration
SECRET_KEY=your_secret_key
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

---

## Features

- **Multi-Address Management**: Primary address + subaddresses with generation
- **Balance Display**: Shows both total balance and unlocked balance (available after 10 confirmations)
- **Transaction History**: Separate incoming/outgoing transaction views with confirmation status
- **Send XMR**: Built-in transaction sending with balance validation
- **QR Code Generation**: Automatic QR code for the latest subaddress for easy receiving
- **QR Code Scanning**: Scan QR codes to automatically fill recipient address and amount
- **Responsive Design**: Clean, professional dark theme
- **Fully Local**: No external dependencies - everything runs locally

---

## QR Code Features

### Receiving Payments

- Automatically generates a QR code for your latest subaddress
- Includes a copy button for the address

### Sending Payments

- Click the QR icon next to the address field to open the scanner
- Supports Monero URI format
- Automatically fills both address and amount fields

---

## Dependencies

- Flask 2.3.3
- monero 1.1.1
- requests 2.31.0
- python-dotenv 1.0.0
- qrcode 7.4.2
- Pillow 10.0.1
