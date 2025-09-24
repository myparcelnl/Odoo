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

    def check_required_data(self, recipient=None, carrier=None):
        recipient_dict = {}
        if recipient:
            # check all required adress fields
            if recipient.country_id:
                recipient_dict['cc'] = recipient.country_id.code
            else:
                raise ValidationError(
                    _('Country code is required for creating a shipment. Please check the delivery address.'))

            if recipient.state_id:
                if recipient.country_id.code in ['US', 'CA', 'AU']:
                    recipient_dict['state'] = recipient.state_id.code
                else:
                    recipient_dict['region'] = recipient.state_id.name
            elif recipient.country_id.code != 'BE':
                raise ValidationError(
                    _('State is required for creating a shipment. Please check the delivery address.'))

            if recipient.city:
                recipient_dict['city'] = recipient.city
            else:
                raise ValidationError(_('City is required for creating a shipment. Please check the delivery address.'))

            # get street number for EU countries
            if recipient.country_id.x_aa_mp_is_european:
                if recipient.street2 and recipient.country_id.code != 'BE':
                    recipient_dict['street'] = recipient.street
                    recipient_dict['number'] = recipient.street2
                else:
                    try:
                        if re.match(r"^(.*?)(\d+)$", recipient.street.strip()):
                            street_number = re.match(r"^(.*?)(\d+)$", recipient.street.strip()).group(2).strip()
                            recipient_dict['street'] = recipient.street.replace(str(street_number), '')
                            recipient_dict['number'] = street_number
                            if recipient.country_id.code == 'BE':
                                recipient_dict['box_number'] = recipient.street2
                            _logger.warning(F'number {street_number}')
                        else:
                            raise ValidationError(
                                _('Street number not found in street field. Please check the delivery address.'))
                    except AttributeError:
                        raise ValidationError(
                            _('Street number not found in street field. Please check the delivery address.'))

            else:
                if recipient.street:
                    recipient_dict['street'] = recipient.street
                    recipient_dict['number'] = ''
                    recipient_dict['street_additional_info'] = recipient.street2
                else:
                    raise ValidationError(
                        _('Complete adress is required for creating a shipment. Please check the delivery address.'))

            if recipient.zip:
                recipient_dict['postal_code'] = recipient.zip
            else:
                raise ValidationError(
                    _('Postal code is required for creating a shipment. Please check the delivery address.'))
            if recipient.name:
                recipient_dict['person'] = recipient.name
                _logger.warning(F'recipient.name {recipient.name}')
            else:
                raise ValidationError(
                    _('Recipient name is required for creating a shipment. Please check the delivery address.'))

            if carrier:
                if carrier.x_aa_mp_phone_send_with_shipment and recipient.phone:
                    recipient_dict['phone'] = recipient.phone
                elif carrier.x_aa_mp_phone_send_with_shipment and not recipient.phone:
                    raise ValidationError(
                        _('Phone number is required for creating a shipment. Please check the delivery address.'))
                if carrier.x_aa_mp_email_send_with_shipment and recipient.email:
                    if re.match(r"^[^@]+@[^@]+\.[^@]+$", recipient.email):
                        recipient_dict['email'] = recipient.email
                    else:
                        raise ValidationError(_('Invalid email address provided. Please check the delivery address.'))
                elif carrier.x_aa_mp_email_send_with_shipment and not recipient.email:
                    raise ValidationError(
                        _('Email address is required for creating a shipment. Please check the delivery address.'))

            return recipient_dict
        else:
            raise ValidationError(
                _('Correct contact information is required for creating a shipment. '
                  'Please check the delivery address.'))

    def _get_insurance_price(self, record, options):
        # Add insurance
        _logger.warning(F'options in post_shipment_body {options}')
        if record:
            if options['insurance'] == 1:
                ins_price = options['insurance_price']
                _logger.warning(F'insurance price in request {ins_price}')
                insured_amount = record.x_aa_mp_insurance_pricelist_id.search(
                    [('id', '=', options['insurance_price'].id)], limit=1)
                if insured_amount:
                    insured_amount = int(insured_amount.x_aa_mp_insurance_selection)
                options['insurance'] = {
                    "amount": insured_amount,
                    "currency": record.currency_id.name or "EUR"
                }
                options.pop('insurance_price')
            else:
                options.pop('insurance')
                options.pop('insurance_price')
        else:
            options.pop('insurance')
            options.pop('insurance_price')

        _logger.warning(F'options in body construction {options}')
        return options

    def _get_customs_declaration(self, record, carrier_code, recipient):
        _logger.warning(F'record._name {record._name}')
        customs_declaration = {}
        if record.sudo()._name == 'sale.order':
            customs_declaration['contents'] = 1
            customs_declaration['invoice'] = record.name
            customs_declaration['weight'] = int(record.shipping_weight * 1000) if record.shipping_weight else (
                ValidationError(_('No shipping weight found. Please check if the product is defined correctly.')))
            items_list = []
            for order_line in record.order_line:
                if order_line.product_id.type != 'service':
                    # Check number of characters per HS code
                    if order_line.product_id.hs_code:
                        if (len(order_line.product_id.hs_code) == 10 and recipient.country_id.cc == 'US') or (
                                len(order_line.product_id.hs_code) in [6, 8, 10]):
                            classification = order_line.product_id.hs_code
                        else:
                            raise ValidationError(_('The HS Code does not have the correct amount of digits.'))
                    else:
                        raise ValidationError(
                            _('No HS Code found for this product. Please check if the product is defined correctly.'))

                    items_list.append({
                        'description': order_line.name,
                        'amount': int(order_line.product_uom_qty),
                        'weight': int(order_line.product_id.weight * 1000) if order_line.product_id.weight else
                        ValidationError(_('No weight found for the product. '
                                          'Please check if the product is defined correctly.')),
                        'item_value': {
                            "amount": int(order_line.price_unit * order_line.product_uom_qty * 100),
                            "currency": record.currency_id.name or "EUR",
                        },
                        'classification': classification,
                        'country': order_line.product_id.country_of_origin.code if
                                   order_line.product_id.country_of_origin else ValidationError(
                                    _('No country of origin found for this product. '
                                    'Please check if the product is defined correctly.')),
                    })

            _logger.warning(F'items for douane declaration {items_list}')
            customs_declaration['items'] = items_list

        elif record.sudo()._name == 'stock.picking':
            customs_declaration['contents'] = 1
            customs_declaration['invoice'] = record.name
            customs_declaration['weight'] = int(record.shipping_weight * 1000) if record.shipping_weight else (
                ValidationError(_('No shipping weight found. Please check if the product is defined correctly.')))
            items_list = []
            for stock_move in record.move_ids:
                order_line = record.sale_id.order_line.search(
                    [('product_template_id', '=', stock_move.product_id.product_tmpl_id.id)], limit=1)

                # Check number of characters per HS code
                if order_line.product_id.hs_code:
                    if (len(order_line.product_id.hs_code) == 10 and recipient.country_id.cc == 'US') or (
                            len(order_line.product_id.hs_code) in [6, 8, 10]):
                        classification = order_line.product_id.hs_code
                    else:
                        raise ValidationError(_('The HS Code does not have the correct amount of digits.'))
                else:
                    raise ValidationError(
                        _('No HS Code found for this product. Please check if the product is defined correctly.'))

                items_list.append({
                    'description': stock_move.product_id.name,
                    'amount': int(stock_move.quantity),
                    'weight': int(stock_move.product_id.weight * 1000) if stock_move.product_id.weight else
                                ValidationError(_('No weight found for the product. '
                                                  'Please check if the product is defined correctly.')),
                    'item_value': {
                        "amount": int(order_line.price_unit * order_line.product_uom_qty * 100),
                        "currency": record.currency_id.name or "EUR",
                    },
                    'classification': classification,
                    'country': stock_move.product_id.country_of_origin.code if stock_move.product_id.country_of_origin
                                else ValidationError(_('No country of origin found for this product. '
                                                       'Please check if the product is defined correctly.')),
                })

            _logger.warning(F'items for douane declaration {items_list}')
            customs_declaration['items'] = items_list

        return customs_declaration

    def post_shipment_body(self, recipient, options, record=None, carrier_code='', carrier=None):
        # Make recipient
        recipient_dict = self.check_required_data(recipient=recipient, carrier=carrier)
        _logger.warning(F'recipient_dict {recipient_dict}')

        if carrier_code == 11:
            if recipient.commercial_partner_id:
                recipient_dict['company'] = recipient.commercial_partner_id.name
            else:
                raise ValidationError(_('Company name is required for creating a shipment. Please check the contact.'))

        # Get Insurance price
        if options and 'insurance' in options:
            options = self._get_insurance_price(record, options)

        shipments = {
            "reference_identifier": record.name,
            "recipient": recipient_dict,
            "options": options,
            "carrier": carrier_code,
        }

        # Shipping weight
        if options and 'weight' in options:
            if not options['weight'] or options['weight'] < 0.01:
                options['weight'] = 0.01  # MyParcel requires a minimum weight of 10 grams
            shipping_weight = {
                "weight": int(options['weight']) * 1000,
            }
            options.pop('weight')
            shipments['physical_properties'] = shipping_weight

        # Multi-collo shipments
        if carrier_code == 1 and record:
            if record._name == 'stock.picking' and record.package_level_ids:
                if len(record.package_level_ids) > 1:
                    shipments['secondary_shipments'] = []

                for sequence, package in enumerate(record.package_level_ids):
                    if sequence == 0:
                        shipments['reference_identifier'] = (
                            '{picking_name} {package_name}'
                        ).format(**{
                            'picking_name': record.name,
                            'package_name': package.package_id.name,
                        })
                    elif sequence > 0:
                        shipments['secondary_shipments'].append({
                            'reference_identifier': (
                                '{picking_name} {package_name}'
                            ).format(**{
                                'picking_name': record.name,
                                'package_name': package.package_id.name,
                            })
                        })

        # Douane information
        if not recipient.country_id.x_aa_mp_is_european:
            customs_declaration = self._get_customs_declaration(record, carrier_code, recipient)
            shipments['customs_declaration'] = customs_declaration

        data = {
            'data': {
                'shipments': [shipments],
            }
        }

        _logger.warning(F'post_shipment_body data {data}')

        return data

    def add_shipping(self, record, options=None, carrier_code='', recipient=None):
        # Get API url and headers
        if options is None:
            options = {}
        url_api = self._get_url('add_shipments')
        headers = self._get_headers('add_shipments')

        if recipient is None:
            recipient = record.partner_id
            if not recipient:
                raise ValidationError(_('No recipient found to create a shipment. Please check the delivery address.'))

        # Get the shipment body
        shipment_body = self.post_shipment_body(recipient=recipient, options=options, record=record,
                                                carrier_code=carrier_code, carrier=self.carrier_id)

        response = requests.post(url_api,
                                 data=json.dumps(shipment_body),
                                 headers=headers)

        json_response = response.json()
        _logger.warning(F'response add shipping {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            if any('Access Denied.' in str(msg) for msg in error_msg):
                raise ValidationError(_('Access Denied. Please check your API key and permissions.'))
            else:
                raise ValidationError(f'ERROR: {error_msg}')

        return json_response

    def get_shipping(self, shipment_id):
        headers = self._get_headers('get_shipments')
        url_api = self._get_url('get_shipments', shipment_id)
        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response get shipping {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            raise ValidationError(f'ERROR: {error_msg}')

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

        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response label {json_response}')

        if json_response.get('errors'):
            error_msg = self._get_error_message(json_response),
            raise ValidationError(f'ERROR: {error_msg}')
        return json_response

    def track_trace(self, shipment_id):
        headers = self._get_headers('track_trace')
        url_api = self._get_url('track_trace', shipment_id)
        response = requests.get(url_api, headers=headers)

        json_response = response.json()
        _logger.warning(F'response track trace {json_response}')

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
