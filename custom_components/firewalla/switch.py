"""Firewalla integration."""
import logging, asyncio, json
import aiohttp
from sshtunnel import open_tunnel

import voluptuous as vol

try:
    from homeassistant.components.switch import SwitchEntity
except:
    from homeassistant.components.switch import \
        SwitchDevice as SwitchEntity
from homeassistant.components.switch import PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration

CONF_POLICY = "policy"
CONF_KEYFILE = "keyfile"
CONF_INVERT = "invert"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_POLICY): cv.string,
    vol.Required(
        CONF_KEYFILE,
        default="/config/firewalla"
    ):cv.string,
    vol.Optional(CONF_INVERT, default=False): cv.boolean
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Firewalla platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    ip_address = config[CONF_HOST]
    async_add_entities([FirewallaPolicy(
        config[CONF_HOST],
        config[CONF_PUBKEY],
        config[CONF_KEYFILE],
        config[CONF_NAME],
        config[CONF_INVERT]
    )])

class FirewallaPolicy(SwitchEntity):
    """Representation of Firewalla Policy as a switch."""

    def __init__(self, host, pubkey, policy, name, invert):
        """Initialize a Firewall policy."""
        self._state = False
        self._name = name
        self._host = host
        self._pubkey = pubkey
        self._policy = policy
        self._available = True
        self._invert = invert
        self.async_update()

    @property
    def name(self):
        """Return the name of the policy if any."""
        return self._name

    @property
    def is_on(self):
        """Return value of state or inverse of value if invert is set to True."""
        if self._invert:
            return not self._state
        else:
            return self._state

    @property
    def should_poll(self):
        return True

    async def async_turn_on(self, **kwargs):
        if self._invert:
            await self._async_turn_off()
        else:
            await self._async_turn_on()

    async def _async_turn_on(self, **kwargs):
        """Instruct the firewalla to enable the policy."""
        with self.getTunnel() as tunnel:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"http://127.0.0.1:{tunnel.local_bind_port}/v1/policy/{self._policy}/enable", data=None) as response:
                    if response.status == 200:
                        try:
                            blob = json.loads(await response.text())
                        except:
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Failed to parse json resonse")
                            return
                        if blob is not None:
                            self._state = True
                            self._available = True
                            _LOGGER.debug(f"[Firewalla Policy {self._policy}] Policy set to enabled")
                        else:
                            self._state = False
                            self._available = False
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy does not appear to be available")
                    else:
                        self._state = False
                        self._available = False
                        _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy turn on has failed")
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        if self._invert:
            await self._async_turn_on()
        else:
            await self._async_turn_off()

    async def _async_turn_off(self, **kwargs):
        """Instruct the firewalla to disable the policy."""
        with self.getTunnel() as tunnel:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"http://127.0.0.1:{tunnel.local_bind_port}/v1/policy/{self._policy}/disable", data=None) as response:
                    if response.status == 200:
                        try:
                            blob = json.loads(await response.text())
                        except:
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Failed to parse json resonse")
                            return
                        if blob is not None:
                            self._state = False
                            self._available = True
                            _LOGGER.debug(f"[Firewalla Policy {self._policy}] Policy set to disabled")
                        else:
                            self._state = False
                            self._available = False
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy does not appear to be available")
                    else:
                        self._state = False
                        self._available = False
                        _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy turn off has failed")
        self.schedule_update_ha_state()

    @property
    def available(self):
        """Return if policy is available."""
        return self._available

    async def async_update(self):
        """Fetch new state data for this policy."""
        await self.update_state()

    async def update_state(self):
        """Update the state."""
        with self.getTunnel() as tunnel:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://127.0.0.1:{tunnel.local_bind_port}/v1/policy/{self._policy}") as response:
                    if response.status == 200:
                        try:
                            blob = json.loads(await response.text())
                        except:
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Failed to parse json resonse")
                            return
                        if blob is not None:
                            if "disabled" in blob and blob["disabled"] == "0":
                                self._state = True
                                self._available = True
                            else:
                                self._state = False
                                self._available = True
                            _LOGGER.debug(f"[Firewalla Policy {self._policy}] Policy status has been updated successfully")

                        else:
                            self._state = False
                            self._available = False
                            _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy does not appear to be available")
                    else:
                        self._state = False
                        self._available = False
                        _LOGGER.warn(f"[Firewalla Policy {self._policy}] Policy turn on has failed")
        self.schedule_update_ha_state()

    def getTunnel(self):
        tunnel = open_tunnel(
            (self._host, 22),
            ssh_username='pi',
            ssh_pkey=self._pubkey,
            remote_bind_address=('127.0.0.1', 8834),
            local_bind_address=('0.0.0.0',)
        )
        return tunnel
