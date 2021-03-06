from homeassistant import config_entries
from homeassistant.const import CONF_IP_ADDRESS, CONF_USERNAME, CONF_PASSWORD
import voluptuous as vol
from .utils import registerController, isRtspStreamWorking
from .const import DOMAIN, ENABLE_MOTION_SENSOR, ENABLE_STREAM, LOGGER, CLOUD_PASSWORD


@config_entries.HANDLERS.register(DOMAIN)
class FlowHandler(config_entries.ConfigFlow):
    """Handle a config flow."""

    VERSION = 4

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TapoOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        return await self.async_step_auth()

    async def async_step_other_options(self, user_input=None):
        errors = {}
        enable_motion_sensor = True
        enable_stream = True
        if user_input is not None:
            enable_motion_sensor = user_input[ENABLE_MOTION_SENSOR]
            enable_stream = user_input[ENABLE_STREAM]
            host = self.tapoHost
            cloud_password = self.tapoCloudPassword
            username = self.tapoUsername
            password = self.tapoPassword
            return self.async_create_entry(
                title=host,
                data={
                    ENABLE_MOTION_SENSOR: enable_motion_sensor,
                    ENABLE_STREAM: enable_stream,
                    CONF_IP_ADDRESS: host,
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                    CLOUD_PASSWORD: cloud_password,
                },
            )

        return self.async_show_form(
            step_id="other_options",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        ENABLE_MOTION_SENSOR,
                        description={"suggested_value": enable_motion_sensor},
                    ): bool,
                    vol.Required(
                        ENABLE_STREAM, description={"suggested_value": enable_stream},
                    ): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_auth_cloud_password(self, user_input=None):
        errors = {}
        cloud_password = ""
        if user_input is not None:
            try:
                cloud_password = user_input[CLOUD_PASSWORD]
                await self.hass.async_add_executor_job(
                    registerController, self.tapoHost, "admin", cloud_password
                )
                self.tapoCloudPassword = cloud_password
                return await self.async_step_other_options()
            except Exception as e:
                if "Failed to establish a new connection" in str(e):
                    errors["base"] = "connection_failed"
                elif str(e) == "Invalid authentication data":
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "unknown"
                    LOGGER.error(e)
        return self.async_show_form(
            step_id="auth_cloud_password",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CLOUD_PASSWORD, description={"suggested_value": cloud_password}
                    ): str,
                }
            ),
            errors=errors,
        )

    async def async_step_auth(self, user_input=None):
        """Confirm the setup."""
        errors = {}
        host = ""
        username = ""
        password = ""
        if user_input is not None:
            try:
                host = user_input[CONF_IP_ADDRESS]
                username = user_input[CONF_USERNAME]
                password = user_input[CONF_PASSWORD]

                rtspStreamWorks = await isRtspStreamWorking(
                    self.hass, host, username, password
                )
                if not rtspStreamWorks:
                    raise Exception("Invalid authentication data")

                self.tapoHost = host
                self.tapoUsername = username
                self.tapoPassword = password
                self.tapoCloudPassword = ""

                try:
                    await self.hass.async_add_executor_job(
                        registerController, host, username, password
                    )
                except Exception as e:
                    if str(e) == "Invalid authentication data":
                        return await self.async_step_auth_cloud_password()
                    else:
                        raise Exception(e)

                return await self.async_step_other_options()

            except Exception as e:
                if "Failed to establish a new connection" in str(e):
                    errors["base"] = "connection_failed"
                elif str(e) == "Invalid authentication data":
                    errors["base"] = "invalid_auth"
                else:
                    errors["base"] = "unknown"
                    LOGGER.error(e)

        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_IP_ADDRESS, description={"suggested_value": host}
                    ): str,
                    vol.Required(
                        CONF_USERNAME, description={"suggested_value": username}
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, description={"suggested_value": password}
                    ): str,
                }
            ),
            errors=errors,
        )


class TapoOptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):
        """Manage the Tapo options."""
        return await self.async_step_auth()

    async def async_step_auth(self, user_input=None):
        """Manage the Tapo options."""
        errors = {}
        username = self.config_entry.data[CONF_USERNAME]
        password = self.config_entry.data[CONF_PASSWORD]
        cloud_password = self.config_entry.data[CLOUD_PASSWORD]
        enable_motion_sensor = self.config_entry.data[ENABLE_MOTION_SENSOR]
        enable_stream = self.config_entry.data[ENABLE_STREAM]
        if user_input is not None:
            try:
                host = self.config_entry.data["ip_address"]
                username = user_input[CONF_USERNAME]
                password = user_input[CONF_PASSWORD]

                if CLOUD_PASSWORD in user_input:
                    cloud_password = user_input[CLOUD_PASSWORD]
                    try:
                        await self.hass.async_add_executor_job(
                            registerController, host, "admin", cloud_password
                        )
                    except Exception as e:
                        LOGGER.error(e)
                        raise Exception("Incorrect cloud password")
                else:
                    cloud_password = ""

                if ENABLE_MOTION_SENSOR in user_input:
                    enable_motion_sensor = user_input[ENABLE_MOTION_SENSOR]
                else:
                    enable_motion_sensor = True

                if ENABLE_STREAM in user_input:
                    enable_stream = user_input[ENABLE_STREAM]
                else:
                    enable_stream = True

                rtspStreamWorks = await isRtspStreamWorking(
                    self.hass, host, username, password
                )
                if not rtspStreamWorks:
                    raise Exception("Invalid authentication data")

                # check if control works with the created account
                if CLOUD_PASSWORD not in user_input and rtspStreamWorks:
                    try:
                        await self.hass.async_add_executor_job(
                            registerController, host, username, password
                        )
                    except Exception as e:
                        LOGGER.error(e)
                        raise Exception("Camera requires cloud password")

                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        ENABLE_STREAM: enable_stream,
                        ENABLE_MOTION_SENSOR: enable_motion_sensor,
                        CONF_IP_ADDRESS: host,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CLOUD_PASSWORD: cloud_password,
                    },
                )
                return self.async_create_entry(title="", data=None)
            except Exception as e:
                if "Failed to establish a new connection" in str(e):
                    errors["base"] = "connection_failed"
                elif str(e) == "Invalid authentication data":
                    errors["base"] = "invalid_auth"
                elif str(e) == "Incorrect cloud password":
                    errors["base"] = "invalid_auth_cloud"
                elif str(e) == "Camera requires cloud password":
                    errors["base"] = "camera_requires_admin"
                else:
                    errors["base"] = "unknown"
                    LOGGER.error(e)

        return self.async_show_form(
            step_id="auth",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME, description={"suggested_value": username}
                    ): str,
                    vol.Required(
                        CONF_PASSWORD, description={"suggested_value": password}
                    ): str,
                    vol.Optional(
                        CLOUD_PASSWORD, description={"suggested_value": cloud_password}
                    ): str,
                    vol.Optional(
                        ENABLE_MOTION_SENSOR,
                        description={"suggested_value": enable_motion_sensor},
                    ): bool,
                    vol.Optional(
                        ENABLE_STREAM, description={"suggested_value": enable_stream},
                    ): bool,
                }
            ),
            errors=errors,
        )
