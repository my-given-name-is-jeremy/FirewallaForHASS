# FirewallaForHASS
Firewalla integration for Home Assistant

## Overview
This integration allows Home Assistant to interact with specific firewalla policies as identified by policy id. A helper script is in this repository
to help you identify the policy id. The act of identifying the correct policy can be a long process of identifying changes when you enable or disable
certain policies. Good luck.

In order to perform the necessary operations against the Firewalla you will need to enable public authentication. This must be done with considartion
to the security implications. Do your research and choose to proceed wisely. The integration uses the public key authentication to establish a tunnel
to the localhost bound unencrypted and unauthenticated api. The integration them performs GET and POST operations against the api to perform the 
requested actions.

Proper operations against the local api can only be performed once the api has been enabled. Place the following script in the 
`~/.firewalla/config/post_main.d/` directory as `app-local.sh`. 

[app-local.sh](https://gist.github.com/my-given-name-is-jeremy/eecb70f2bee1f36621b54bdeb87a23d9)

Use the following command to enable execution of the file.

```
# chmod +x app-local.sh
```

## Installation
Download the latest from the repository and place the `firewalla` directory in the custom_components directory of your Home Assistant installation.
Generate a rsa keypair on your Home Assistant server so you don't have to copy/paste the private key.
`# ssh-keygen -f /config/firewalla`
A `firewalla.pub` file will be created. Copy that file's contents to your firewalla into a file call `authorized_keys` in the `/home/pi/.ssh/` directory.

```
# chown pi:pi authorized_keys
# chmod 0600 authorized_keys
```

In your configuration.yaml file you will create new switch devices for your firewalla policies you want to interact with.

```
switch:
  - platform: firewalla
    name: Clever name
    policy: <integer for the policy>
    host: <IP address for firewalla>
```

If you add the `invert: <boolean>` property you can invert the logic. A disabled or "paused" policy will show as "On" in Home Assistant
and will behave appropriately when switched.

A `keyfile: <path to private key>` is an available property as well and defaults to `/config/firewalla`.

