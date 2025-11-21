"""Provide the config flow."""
from homeassistant.core import callback
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector
import voluptuous as vol
import logging
from .const import *
import os
import os.path
from homeassistant.helpers.storage import STORAGE_DIR
import ytmusicapi
try:
	from ytmusicapi.helpers import SUPPORTED_LANGUAGES
except ImportError:
	SUPPORTED_LANGUAGES = ['en']
import json
import os

from collections import OrderedDict

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class yTubeMusicFlowHandler(config_entries.ConfigFlow):
	"""Provide the initial setup."""

	CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
	VERSION = 1

	def __init__(self):
		"""Provide the init function of the config flow."""
		# Called once the flow is started by the user
		self._errors = {}

	# entry point from config start
	async def async_step_user(self, user_input=None):   # pylint: disable=unused-argument
		return await async_common_step_user(self,user_input)
		

	async def async_step_oauth(self, user_input=None):   # pylint: disable=unused-argument
		return await async_common_step_oauth(self, user_input)

	# we get here after the user click submit on the oauth screem
	# lets check if oauth worked
		
	# will be called by sending the form, until configuration is done
	async def async_step_finish(self,user_input=None):
		return await async_common_step_finish(self, user_input)
	

	async def async_step_adv_finish(self,user_input=None):
		return await async_common_step_adv_finish(self, user_input)
		

	# TODO .. what is this good for?
	async def async_step_import(self, user_input):  # pylint: disable=unused-argument
		"""Import a config entry.

		Special type of import, we're not actually going to store any data.
		Instead, we're going to rely on the values that are in config file.
		"""
		if self._async_current_entries():
			return self.async_abort(reason="single_instance_allowed")

		return self.async_create_entry(title="configuration.yaml", data={})

	@staticmethod
	@callback
	def async_get_options_flow(config_entry):
		"""Call back to start the change flow."""
		return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
	"""Change an entity via GUI."""

	def __init__(self, config_entry):
		"""Set initial parameter to grab them later on."""
		# store old entry for later
		self.data = dict(config_entry.options or config_entry.data)
		self.data[CONF_HEADER_PATH+"_old"] = self.data[CONF_HEADER_PATH]


	# will be called by sending the form, until configuration is done
	async def async_step_init(self, user_input=None):   # pylint: disable=unused-argument
		"""Call this as first page."""
		user_input = self.data
		return await async_common_step_user(self,user_input, option_flow = True)
	
	async def async_step_oauth(self, user_input=None):   # pylint: disable=unused-argument
		return await async_common_step_oauth(self, user_input, option_flow = True)

		
	# will be called by sending the form, until configuration is done
	async def async_step_finish(self,user_input=None):
		return await async_common_step_finish(self, user_input, option_flow = True)
	

	async def async_step_adv_finish(self,user_input=None):
		return await async_common_step_adv_finish(self, user_input, option_flow = True)
	

async def async_common_step_user(self, user_input=None, option_flow = False):
	self._errors = {}
	#_LOGGER.error("step user was just called")
	"""Call this as first page."""
	if(user_input == None):
		user_input = dict()
		user_input[CONF_NAME] = DOMAIN
	self.data = user_input
	return self.async_show_form(step_id="oauth", data_schema=vol.Schema(await async_create_form(self.hass,user_input,0, option_flow)), errors=self._errors)


async def async_common_step_oauth(self, user_input=None, option_flow = False):   # pylint: disable=unused-argument
	# we should have received the cookie data
	self._errors = {}
	#_LOGGER.error("step oauth was just called")
	if user_input is not None:
		self.data.update(user_input)
		if CONF_NAME in user_input:
			self.data[CONF_NAME] = user_input[CONF_NAME].replace(DOMAIN_MP+".","") # make sure to erase "media_player.bla" -> bla

	return self.async_show_form(step_id="finish", data_schema=vol.Schema(await async_create_form(self.hass,user_input,1, option_flow)), errors=self._errors)



async def async_common_step_finish(self,user_input=None, option_flow = False):
	self._errors = {}
	#_LOGGER.error("step finish was just called")
	self.data.update(user_input)

	# Validate cookies
	_LOGGER.debug("Starting cookie validation in config_flow")
	try:
		ret, msg, api = await async_try_login(self.hass, '', brand_id=self.data.get(CONF_BRAND_ID, ''), language=self.data.get(CONF_API_LANGUAGE, 'en'), oauth=None, po_token=self.data.get(CONF_PO_TOKEN, ''), visitor_data=self.data.get(CONF_VISITOR_DATA, ''), cookies=self.data.get(CONF_COOKIE, ''))
		_LOGGER.debug("async_try_login returned: ret=%s, msg='%s', api is not None: %s", ret, msg, api is not None)
		if ret and 'base' in ret:
			error_code = ret['base']
			if error_code == ERROR_FORMAT:
				self._errors["base"] = ERROR_INVALID_COOKIE
			elif error_code == ERROR_COOKIE:
				self._errors["base"] = ERROR_COOKIE_FORMAT
			elif error_code == ERROR_CONTENTS:
				self._errors["base"] = ERROR_MISSING_PARAM
			elif error_code == ERROR_FORBIDDEN:
				self._errors["base"] = ERROR_INVALID_COOKIE
			else:
				self._errors["base"] = error_code
			return self.async_show_form(step_id="finish", data_schema=vol.Schema(await async_create_form(self.hass,self.data,1, option_flow)), errors=self._errors)
	except Exception as e:
		self._errors["base"] = ERROR_GENERIC
		return self.async_show_form(step_id="finish", data_schema=vol.Schema(await async_create_form(self.hass,self.data,1, option_flow)), errors=self._errors)

	# Set header path if not set
	if CONF_HEADER_PATH not in self.data or not self.data[CONF_HEADER_PATH]:
		self.data[CONF_HEADER_PATH] = os.path.join(self.hass.config.path(STORAGE_DIR), DEFAULT_HEADER_FILENAME + self.data[CONF_NAME].replace(' ', '_') + '.json')

	# Save cookie data to file
	cookie_data = {
		'cookies': self.data.get(CONF_COOKIE, ''),
		'po_token': self.data.get(CONF_PO_TOKEN, ''),
		'visitor_data': self.data.get(CONF_VISITOR_DATA, '')
	}
	_LOGGER.debug("Saving cookie_data to %s: cookies length=%d", self.data[CONF_HEADER_PATH], len(cookie_data['cookies']))
	await self.hass.async_add_executor_job(lambda: (
		os.makedirs(os.path.dirname(self.data[CONF_HEADER_PATH]), exist_ok=True),
		json.dump(cookie_data, open(self.data[CONF_HEADER_PATH], 'w'))
	))
	_LOGGER.debug("Cookie data saved to %s", self.data[CONF_HEADER_PATH])

	if(self.data.get(CONF_ADVANCE_CONFIG, False)):
		return self.async_show_form(step_id="adv_finish", data_schema=vol.Schema(await async_create_form(self.hass,self.data,4, option_flow)), errors=self._errors)
	elif option_flow:
		return self.async_create_entry(data = self.data)
	else:
		return self.async_create_entry(title="yTubeMusic "+self.data[CONF_NAME].replace(DOMAIN,''), data=self.data)
	

async def async_common_step_adv_finish(self,user_input=None, option_flow = False):
	self._errors = {}
	#_LOGGER.error("step adv finish was just called")
	self.data.update(user_input)
	if option_flow:
		return self.async_create_entry(data = self.data)
	else:
		return self.async_create_entry(title="yTubeMusic "+self.data[CONF_NAME].replace(DOMAIN,''), data=self.data)

	
async def async_create_form(hass, user_input, page=1, option_flow = False):
	"""Create form for UI setup."""
	user_input = ensure_config(user_input)
	data_schema = OrderedDict()
	try:
		languages = list(SUPPORTED_LANGUAGES)
	except (NameError, TypeError, AttributeError):
		languages = ['en']

	if(page == 0):
		data_schema[vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, DOMAIN))] = str # name of the component without domain
	elif(page == 1):
		data_schema[vol.Required(CONF_COOKIE, default=user_input.get(CONF_COOKIE, ''))] = str # cookie string
		data_schema[vol.Required(CONF_PO_TOKEN)] = vol.All(str, vol.Length(min=1)) # PO token (required for bot detection bypass)
		data_schema[vol.Required(CONF_VISITOR_DATA)] = vol.All(str, vol.Length(min=1)) # Visitor data (required for bot detection bypass)
	elif(page == 3):
		# Generate a list of excluded entities.
		# This method is more reliable because it won't become invalid 
		# if users modify entity IDs, and it supports multiple instances.
		_exclude_entities = []
		if (_ytm := hass.data.get(DOMAIN)) is not None:
			for _ytm_player in _ytm.values():
				if DOMAIN_MP in _ytm_player:
					_exclude_entities.append(_ytm_player[DOMAIN_MP].entity_id)

		data_schema[vol.Required(CONF_RECEIVERS,default=user_input.get(CONF_RECEIVERS, ''))] = selector({
				"entity": {
					"multiple": "true",
					"filter": [{"domain": DOMAIN_MP}],
					"exclude_entities": _exclude_entities
				}
			})
		data_schema[vol.Required(CONF_API_LANGUAGE, default=user_input.get(CONF_API_LANGUAGE, DEFAULT_API_LANGUAGE))] = selector({
				"select": {
					"options": languages,
					"mode": "dropdown",
					"sort": True
				}
			})
		data_schema[vol.Required(CONF_HEADER_PATH, default=user_input.get(CONF_HEADER_PATH, ''))] = str # file path of the header
		data_schema[vol.Required(CONF_ADVANCE_CONFIG, default=user_input.get(CONF_ADVANCE_CONFIG, False))] = vol.Coerce(bool) # show page 2

	elif(page == 4):
		data_schema[vol.Optional(CONF_SHUFFLE, default=user_input[CONF_SHUFFLE])] = vol.Coerce(bool) # default shuffle, TRUE/FALSE
		data_schema[vol.Optional(CONF_SHUFFLE_MODE, default=user_input[CONF_SHUFFLE_MODE])] = selector({  # choose default shuffle mode
				"select": {
					"options": ALL_SHUFFLE_MODES,
					"mode": "dropdown"
				}
			})
		data_schema[vol.Optional(CONF_LIKE_IN_NAME, default=user_input[CONF_LIKE_IN_NAME])] = vol.Coerce(bool) # default like_in_name, TRUE/FALSE
		data_schema[vol.Optional(CONF_DEBUG_AS_ERROR, default=user_input[CONF_DEBUG_AS_ERROR])] = vol.Coerce(bool) # debug_as_error, TRUE/FALSE
		data_schema[vol.Optional(CONF_LEGACY_RADIO, default=user_input[CONF_LEGACY_RADIO])] = vol.Coerce(bool) # default radio generation typ
		data_schema[vol.Optional(CONF_SORT_BROWSER, default=user_input[CONF_SORT_BROWSER])] = vol.Coerce(bool) # sort browser results
		data_schema[vol.Optional(CONF_INIT_EXTRA_SENSOR, default=user_input[CONF_INIT_EXTRA_SENSOR])] = vol.Coerce(bool) # default radio generation typ
		data_schema[vol.Optional(CONF_INIT_DROPDOWNS,default=user_input[CONF_INIT_DROPDOWNS])] = selector({  # choose dropdown(s)
				"select": {
					"options": ALL_DROPDOWNS,
					"multiple": "true"
				}
			})
		#  add for the old inputs.
		for _old_conf_input in OLD_INPUTS.values():
			if user_input.get(_old_conf_input) is not None:
				data_schema[vol.Optional(_old_conf_input, default=user_input[_old_conf_input])] = str

		data_schema[vol.Optional(CONF_TRACK_LIMIT, default=user_input[CONF_TRACK_LIMIT])] = vol.Coerce(int)
		data_schema[vol.Optional(CONF_MAX_DATARATE, default=user_input[CONF_MAX_DATARATE])] = vol.Coerce(int)
		data_schema[vol.Optional(CONF_BRAND_ID, default=user_input[CONF_BRAND_ID])] = str # brand id

		data_schema[vol.Optional(CONF_PROXY_PATH, default=user_input[CONF_PROXY_PATH])] = str # select of input_boolean -> continuous on/off
		data_schema[vol.Optional(CONF_PROXY_URL, default=user_input[CONF_PROXY_URL])] = str # select of input_boolean -> continuous on/off
		data_schema[vol.Optional(CONF_PO_TOKEN, default=user_input[CONF_PO_TOKEN])] = str # PO token for YouTube Music API
		data_schema[vol.Optional(CONF_VISITOR_DATA, default=user_input[CONF_VISITOR_DATA])] = str # Visitor data for YouTube Music API

	return data_schema

