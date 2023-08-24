# outline-vpn-api

A Python API wrapper for [Outline VPN](https://getoutline.org/)

[![Test](https://github.com/jadolg/outline-vpn-api/actions/workflows/test.yml/badge.svg)](https://github.com/jadolg/outline-vpn-api/actions/workflows/test.yml) ![](https://img.shields.io/pypi/dm/outline-vpn-api.svg)

## How to use

```python
from outline_vpn.outline_vpn import OutlineVPN

# Setup the access with the API URL (Use the one provided to you after the server setup)
client = OutlineVPN(api_url="https://2.59.183.37:38411/bVPmyljNmp4S0sDJItaBXA",
                    cert_sha256="e6624996-b175-434a-bffa-e7d046303dbb")

# Get all access URLs on the server
for key in client.get_keys():
    print(key.access_url)

# Create a new key
new_key = client.create_key()

# Rename it
client.rename_key(new_key.key_id, "new_key")

# Delete it
client.delete_key(new_key.key_id)

# Set a monthly data limit for a key (20MB)
client.add_data_limit(new_key.key_id, 1000 * 1000 * 20)

# Remove the data limit
client.delete_data_limit(new_key.key_id)

```
