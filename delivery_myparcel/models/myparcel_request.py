# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################
import odoo.release
from odoo import _
from odoo.exceptions import ValidationError
import base64
import re
import logging
import requests
import json

_logger = logging.getLogger(__name__)

MYPARCEL_BASE_API_URL = 'https://api.myparcel.nl'


class MyParcelRequest:

    def __init__(self, carrier_id, module_version=odoo.release.version):
        # Initializer
        self.url = MYPARCEL_BASE_API_URL
        self.module_version = module_version
        self.odoo_version = odoo.release.version
        self.carrier_id = carrier_id

    def _get_url(self, request_type, shipment_id=None):
        if request_type == 'add_shipments':
            url_path = f'{self.url}/shipments'
        elif request_type == 'get_shipments':
            url_path = f'{self.url}/shipments?id={shipment_id}'
        elif request_type == 'delete_shipments':
            url_path = f'{self.url}/shipments/{shipment_id}'
        elif request_type == 'get_label':
            url_path = f'{self.url}/shipment_labels/{shipment_id}'
        elif request_type == 'track_trace':
            url_path = f'{self.url}/tracktraces/{shipment_id}'
        else:
            raise ValidationError(_('Could not find API URL for this request.'))
        return url_path

    def _get_user_agent(self):
        user_agent = f'MyParcel-Odoo/{self.odoo_version} delivery_myparcel/{self.module_version}'
        return user_agent

    def _get_headers(self, call=''):
        api_key = self.carrier_id.x_aa_mp_api_key
        api_key_encoded = base64.b64encode(api_key.encode('utf-8')).decode('utf-8')

        if call == 'add_shipments':
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Content-Type': 'application/vnd.shipment+json;version=1.1;charset=utf-8',
                'Authorization': 'bearer ' + api_key_encoded,
            }
        elif call == 'get_shipments':
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': 'bearer ' + api_key_encoded,
            }
        elif call == 'delete_shipments':
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Authorization': 'bearer ' + api_key_encoded,
            }
        elif call == 'get_label':
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Accept': 'application/json;charset=utf-8',
                'Authorization': 'bearer ' + api_key_encoded,
            }
        elif call == 'track_trace':
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Accept': 'application/json;charset=utf-8',
                'Authorization': 'bearer ' + api_key_encoded,
            }
        else:
            # Using default headers if the call is not recognized
            headers = {
                'User-Agent': self._get_user_agent(),
                'Host': 'api.myparcel.nl',
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': 'bearer ' + api_key_encoded,
            }

        return headers

    def post_shipment_body(self, recipient, options, reference='', carrier_code=''):
        if recipient.street2:
            street = recipient.street
            street_number = recipient.street2
        else:
            try:
                if re.match(r"^(.*?)(\d+)$", recipient.street.strip()):
                    street_number = re.match(r"^(.*?)(\d+)$", recipient.street.strip()).group(2).strip()
                    street = recipient.street.replace(str(street_number), '')
                    _logger.warning(F'street_number {street_number}')
                else:
                    raise ValidationError(_('Street number not found in street field. Please check the address.'))
            except AttributeError:
                raise ValidationError(
                    _('Street not found in address. Please confirm you have a valid (delivery)address.'))

        # Make recipient
        recipient_dict = {
            "cc": recipient.country_id.code or "NL",
            "region": recipient.state_id.name or "",
            "city": recipient.city or "",
            "street": street or "",
            "number": street_number or "",
            "postal_code": recipient.zip or "",
            "person": recipient.name or "",
            "phone": recipient.phone or "",
            "email": recipient.email or "",
        }

        if carrier_code == 11:
            recipient_dict['company'] = recipient.commercial_partner_id.name or ""

        shipments = {
            "reference_identifier": reference,
            "recipient": recipient_dict,
            "options": options,
            "carrier": carrier_code,
        }

        data = {
            'data': {
                'shipments': [shipments],
            }
        }

        return data

    def add_shipping(self, record, options=None, carrier_code='', recipient=None):
        # Get API url and headers
        if options is None:
            options = {}
        url_api = self._get_url('add_shipments')
        headers = self._get_headers('add_shipments')
        _logger.warning(F'carrier_id {self.carrier_id}')

        if recipient is None:
            recipient = record.partner_id

        # Get the shipment body
        shipment_body = self.post_shipment_body(recipient=recipient, options=options, reference=record.name,
                                                carrier_code=carrier_code)

        _logger.warning(F'url_api {url_api}')
        _logger.warning(F'headers {headers}')
        _logger.warning(F'shipment_body {shipment_body}')

        response = requests.post(url_api,
                                 data=json.dumps(shipment_body),
                                 headers=headers)

        json_response = response.json()
        _logger.warning(F'response check {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            raise ValidationError(f'ERROR: {error_msg}')

        return json_response

    def get_shipping(self, shipment_id):
        headers = self._get_headers('get_shipments')
        url_api = self._get_url('get_shipments', shipment_id)
        _logger.warning(F'url_api {url_api}')
        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response check get {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            ValidationError(f'ERROR: {error_msg}')
            return 'Error'

        return json_response

    def delete_shipment(self, shipment_id):
        headers = self._get_headers('delete_shipments')
        url_api = self._get_url('delete_shipments', shipment_id)

        response = requests.delete(url_api, headers=headers)
        _logger.warning(F'response delete shipment : {response.status_code}')

        if response.status_code != 204:
            json_response = response.json()
            _logger.warning(F'response delete {json_response}')

            if json_response.get('errors'):
                error_msg = self._get_error_message(json_response)
                return {
                    'success': False,
                    'error_message': error_msg
                }

        else:
            return {
                'success': True,
                'error_message': False
            }

    def get_label(self, shipment_id, label_size=None, label_position=None):
        headers = self._get_headers('get_label')
        url_api = self._get_url('get_label', shipment_id)
        if label_size and label_position:
            url_api += f'?format={label_size}&positions={label_position}'

        _logger.warning(F'url_api {url_api}')
        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response check label {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            raise ValidationError(f'ERROR: {error_msg}')
        return json_response

    def track_trace(self, shipment_id):
        headers = self._get_headers('track_trace')
        url_api = self._get_url('track_trace', shipment_id)

        _logger.warning(F'url_api {url_api}')
        _logger.warning(F'headers {headers}')
        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response check label {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            raise ValidationError(f'ERROR: {error_msg}')
        return json_response

    def custom_request(self, method='GET', path='/', custom_headers=False):
        """
        Make a custom request to the MyParcel API.
        :param method: HTTP method (GET, POST, DELETE, etc.)
        :param path: API endpoint path
        :param custom_headers: Custom headers to include in the request
        :return: Response from the API
        """
        url = f'{self.url}{path}'
        if not custom_headers:
            custom_headers = self._get_headers()

        response = requests.request(method, url, headers=custom_headers)

        return response

    def download_file(self, url):
        return requests.get(url).content

    @staticmethod
    def _get_error_message(response):
        msgs = []

        message = response.get('message', '')
        msgs.append(message)

        all_errors = response.get('errors')
        for errors in all_errors:

            human_errors = errors.get('human')
            if human_errors:
                if isinstance(human_errors, list):
                    msgs += human_errors
                else:
                    msgs.append(human_errors)
            else:
                for key, error in errors.items():
                    if not isinstance(error, dict):
                        continue

                    human_errors = error.get('human')
                    if human_errors:
                        if isinstance(human_errors, list):
                            msgs += human_errors
                        else:
                            msgs.append(human_errors)

                    err_msg = error.get('message')
                    if err_msg:
                        msgs.append(err_msg)

            err_msg = errors.get('message')
            if err_msg:
                msgs.append(err_msg)

        msgs = list(set(msgs))

        return '\n'.join(msgs)
