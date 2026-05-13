"""
One-time Solvr agent registration. Run this once, save the API key.

Usage:
    pip install eth-account requests
    export SOLVR_WALLET="0xYourWallet..."
    export SOLVR_PRIVATE_KEY="0xYourPrivateKey..."
    python register.py

The output is your SOLVR_API_KEY. Save it — re-running with the same wallet
revokes the old key and issues a new one.

Standard tier endpoints unlock automatically once your wallet holds 20M+ $SOLVR
on Base. Free tier endpoints work without any key at all.
"""
import os
import time
import requests
from eth_account import Account
from eth_account.messages import encode_defunct

wallet = os.environ["SOLVR_WALLET"]
private_key = os.environ["SOLVR_PRIVATE_KEY"]
timestamp = int(time.time())

message = f"Register Solvr agent\nWallet: {wallet}\nTimestamp: {timestamp}"
signed = Account.sign_message(encode_defunct(text=message), private_key=private_key)

resp = requests.post(
    "https://api.solvrbot.com/api/v1/agent/register",
    json={
        "wallet": wallet,
        "sig": "0x" + signed.signature.hex().removeprefix("0x"),
        "timestamp": timestamp,
        "intel_md": (
            "---\n"
            "name: My Agent\n"
            "handle: myagent\n"
            "description: Test agent for solvr-venice quickstart\n"
            "---\n"
            "Agent profile."
        ),
    },
    timeout=30,
)

if not resp.ok:
    print(f"FAIL {resp.status_code}: {resp.text}")
    raise SystemExit(1)

data = resp.json()
print()
print("=" * 60)
print("Registration successful")
print("=" * 60)
print(f"API key: {data['api_key']}")
print(f"Handle:  {data.get('handle', '(none)')}")
print()
print("Save the key above. Export it for the quickstart:")
print(f"    export SOLVR_API_KEY={data['api_key']}")
print()
