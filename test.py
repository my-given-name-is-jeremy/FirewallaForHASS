"""
The following script will allow you identify your policy id
supply the necessary value below to allow the script to
connect to your Firewall and print a list of all your policies

A json blob like the following will print out.

{
  "list": [
    {
      "tag": [
        "tag:1"
      ],
      "type": "dns",
      "action": "allow",
      "notes": "",
      "target": "github.com",
      "dnsmasq_only": false,
      "upnp": false,
      "direction": "bidirection",
      "timestamp": "1604969191.165",
      "pid": "23",
      "activatedTime": "1604969191.207"
    }
  ]
}

The "pid" is the policy id you will use to add this policy
to Home Assistant. Add a note to the policy you are trying
to find, execute this script and fine the block that
correlates with your note.
"""

REMOTE_SERVER_IP = "<IP address of Firewalla>"
REMOTE_SERVER_USER = "pi"
REMOTE_SERVER_PUBKEY = "/config/firewalla"
REMOTE_BIND_PORT = 8834

import requests, json, aiohttp, asyncio
from sshtunnel import open_tunnel

async def main():
    with open_tunnel(
        (REMOTE_SERVER_IP, 22),
        ssh_username=REMOTE_SERVER_USER,
        ssh_pkey=REMOTE_SERVER_PUBKEY,
        remote_bind_address=('127.0.0.1', REMOTE_BIND_PORT),
        local_bind_address=('0.0.0.0',)
    ) as tunnel:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:{tunnel.local_bind_port}/v1/policy/list") as response:
                if response.status == 200:
                    policies = json.loads(await response.text())
                    print(json.dumps(policies, indent=2))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
