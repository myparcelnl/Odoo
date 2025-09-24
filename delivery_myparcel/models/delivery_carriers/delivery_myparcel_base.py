# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, api, _
from odoo.tools import pdf
from odoo.addons.delivery_myparcel.data.myparcel_static_data import MYPARCEL_DELIVERY_TYPES, \
    SENDMYPARCEL_DELIVERY_TYPES, MYPARCEL_CARRIER_CODES, MYPARCEL_DELIVERY_CODES, MYPARCEL_LABEL_POSITIONS_CODES, \
    MYPARCEL_BASE_TRACK_TRACE_URL
from odoo.exceptions import UserError, ValidationError
from ..myparcel_request import MyParcelRequest
import logging
from urllib.parse import urlparse, parse_qs

_logger = logging.getLogger()


class BaseProviderMyParcel(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    x_aa_mp_is_myparcel = fields.Boolean(string='Is MyParcel Carrier', compute='_compute_is_myparcel_carrier')
    x_aa_mp_is_sendmyparcel = fields.Boolean(string='Is SendMyParcel Carrier', compute='_compute_is_myparcel_carrier')
    x_aa_mp_platform = fields.Selection([('myparcel', 'MyParcel NL'), ('sendmyparcel', 'MyParcel BE')],
                                        string='MyParcel Platform', required=True, store=True)

    # General settings - Algemene settings
    x_aa_mp_api_key = fields.Char(string='API Key')

    # Order settings - Bestelling settings
    x_aa_mp_ordermodus = fields.Boolean(string='Order Mode', default=False)
    x_aa_mp_email_send_with_shipment = fields.Boolean(string='Add Email to Shipment', default=False)
    x_aa_mp_phone_send_with_shipment = fields.Boolean(string='Add Phone to Shipment', default=False)

    # Label settings
    x_aa_mp_label_position = fields.Selection([('top_left', 'Top Left'), ('top_right', 'Top Right'),
                                               ('bottom_left', 'Bottom Left'), ('bottom_right', 'Bottom Right')],
                                              string='Label position', default='top_left', required=True)
    x_aa_mp_label_size = fields.Selection([('A4', 'Standard Printer (A4)'), ('A6', 'Labelprinter (A6)')],
                                          string='Label size', default='A4', required=True)
    x_aa_mp_direct_label = fields.Boolean(string='Direct Label', default=False,
                                          help="If enabled, the label will be printed directly without confirmation.")

    # Package type settings
    x_aa_mp_package_type_id = fields.Many2one('stock.package.type', string='Package Type',
                                              help="Select the package type to use for MyParcel shipments.",
                                              required=True)

    # Customs settings - Douane settings
    x_aa_mp_package_type = fields.Char(string='Package type dropdown should be here')

    # Checkout settings
    x_aa_mp_order_options = fields.Char(string='Checkout settings should be here')

    # Other settings - Overige settings
    x_aa_mp_overige_settings = fields.Char(string='Other settings should be here')

    # Insurance settings
    x_aa_mp_insurance_pricelist_id = fields.One2many(
        comodel_name='myparcel.insurance.price',
        inverse_name='carrier_id',
        string='Delivery Insurance Pricelist',
    )

    # Delivery pricing
    x_aa_mp_delivery_price = fields.Selection([('dynamic', 'Dynamic pricing'), ('fixed', 'Fixed Price')],
                                              string='Pricing method', default='dynamic', required=True)
    x_aa_mp_fixed_price = fields.Monetary(string='Fixed Price (MyParcel)', default=0.0, currency_field='currency_id',
                                          help="The fixed price for the delivery method.")
    x_aa_mp_age_control_price = fields.Monetary(string='Age Verification Price (18+)', default=0.0,
                                                currency_field='currency_id')
    x_aa_mp_signing_price = fields.Monetary(string='Signature Price', default=0.0, currency_field='currency_id')
    x_aa_mp_only_receiver_price = fields.Monetary(string='Receiver Only Price', default=0.0,
                                                  currency_field='currency_id')
    x_aa_mp_large_package_price = fields.Monetary(string='Larger than 100x70x58 cm Price', default=0.0,
                                                  currency_field='currency_id')
    x_aa_mp_direct_return_price = fields.Monetary(string='Direct Return Price', default=0.0,
                                                  currency_field='currency_id')

    @api.depends('delivery_type', 'x_aa_mp_platform')
    def _compute_is_myparcel_carrier(self):
        for rec in self:
            rec.x_aa_mp_is_myparcel = (rec.delivery_type and rec.delivery_type in MYPARCEL_DELIVERY_TYPES and
                                       rec.x_aa_mp_platform == 'myparcel')
            rec.x_aa_mp_is_sendmyparcel = (rec.delivery_type and rec.delivery_type in SENDMYPARCEL_DELIVERY_TYPES and
                                           rec.x_aa_mp_platform == 'sendmyparcel')

    def get_myparcel_request(self, carrier_id, module_version):
        return MyParcelRequest(carrier_id=carrier_id, module_version=module_version)

    def base_myparcel_rate_shipment(self, order, options=None, delivery_type=False):
        delivery_price = 0.0
        if self.x_aa_mp_delivery_price == 'fixed':
            delivery_price = self.x_aa_mp_fixed_price
            extra_price = 0.0
            _logger.warning(F'options {options}')
            if 'age_check' in options and options['age_check'] == 1:
                if self.x_aa_mp_age_control_price:
                    extra_price += self.x_aa_mp_age_control_price
            if 'only_recipient' in options and options['only_recipient'] == 1:
                if self.x_aa_mp_only_receiver_price:
                    extra_price += self.x_aa_mp_only_receiver_price
            if 'signature' in options and options['signature'] == 1:
                if self.x_aa_mp_signing_price:
                    extra_price += self.x_aa_mp_signing_price
            if 'return' in options and options['return'] == 1:
                if self.x_aa_mp_direct_return_price:
                    extra_price += self.x_aa_mp_direct_return_price
            if 'large_format' in options and options['large_format'] == 1:
                if self.x_aa_mp_large_package_price:
                    extra_price += self.x_aa_mp_large_package_price
            if 'insurance' in options and options['insurance'] == 1:
                insurance_price_opt = options['insurance_price']
                _logger.warning(F'insurance_price_opt {insurance_price_opt}')
                if options['insurance_price']:
                    insurance_price = self.x_aa_mp_insurance_pricelist_id.search(
                        [('carrier_id', '=', self.id), ('id', '=', options['insurance_price'].id)], limit=1).price
                    _logger.warning(F'insurance_price {insurance_price}')
                    extra_price += int(insurance_price)
            if 'same_day_delivery' in options and options['same_day_delivery'] == 1:
                if self.x_aa_mp_sameday_delivery_price:
                    extra_price += self.x_aa_mp_sameday_delivery_price
            delivery_price += extra_price
            _logger.warning(F'delivery_price myparcel_rate_shipment {delivery_price}')
            return {
                'success': True,
                'price': delivery_price,
                'error_message': False,
                'warning_message': False
            }

        elif self.x_aa_mp_delivery_price == 'dynamic':
            _logger.warning(F'delivery_price myparcel_rate_shipment {delivery_price}')
            return self.myparcel_get_shipping_rate(order, options, delivery_type)
        else:
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Error: this delivery method is not available.'),
                'warning_message': False,
            }

    def myparcel_get_shipping_rate(self, record, options=None, delivery_type=False):
        myparcel_request = self.get_myparcel_request(carrier_id=self, module_version=self.get_module_version())
        # Add shipment
        result = myparcel_request.add_shipping(record, options, self._get_carrier_code(delivery_type=delivery_type),
                                               recipient=record.partner_shipping_id)
        _logger.warning(F'result from add_shipping {result}')

        # Shipment MyParcel id
        shipment_id = None
        if result != 'Error':
            for shipment_ids in result.get('data').get('ids'):
                shipment_id = shipment_ids.get('id')
                _logger.warning(F'shipment_id {shipment_id}')

        # Get shipment info
        if shipment_id:
            shipment_info = myparcel_request.get_shipping(shipment_id)
            if 'postnl' in delivery_type:
                shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                if shipment_info['data']['shipments'][0]['secondary_shipments']:
                    for secondary_shipment in shipment_info['data']['shipments'][0]['secondary_shipments']:
                        secondary_shipment_price = secondary_shipment['price']['amount'] / 100
                        shipment_price += secondary_shipment_price
            else:
                shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                shipment_status = shipment_info['data']['shipments'][0]['status']

            result = myparcel_request.delete_shipment(shipment_id)

            if not result['success']:
                return {
                    'success': False,
                    'price': 0.0,
                    'error_message': _(f"Error: could not delete shipment. {result['error_message']}"),
                    'warning_message': False,
                }
            if shipment_price:
                return {'success': True,
                        'price': shipment_price,
                        'error_message': False,
                        'warning_message': False}
        else:
            return {
                'success': False,
                'price': 0.0,
                'error_message': _('Error: this delivery method is not available as no shipment ID was found. '
                                   'This could be caused by a wrong address or wrong delivery options. '
                                   'Check again to make sure there is no wrong input.'),
                'warning_message': False,
            }

    def action_check_myparcel_api(self):
        if not self.x_aa_mp_api_key:
            raise UserError("API key is missing.")
        myparcel_request = self.get_myparcel_request(carrier_id=self, module_version=self.get_module_version())
        response_check = myparcel_request.custom_request()
        json_response = response_check.json()

        if json_response.get('status') == 'OK':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Successful',
                    'message': 'API connection to MyParcel is working.',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Error',
                    'message': 'Check API key.',
                    'sticky': True,
                    'type': 'danger',
                }
            }

    def base_myparcel_send_shipping(self, pickings, options=None, delivery_type=False):
        res = []
        myparcel_request = self.get_myparcel_request(carrier_id=self, module_version=self.get_module_version())
        if not pickings.x_aa_mp_shipping_id:
            result = myparcel_request.add_shipping(pickings, options,
                                                   self._get_carrier_code(delivery_type=delivery_type),
                                                   recipient=pickings.partner_id)
            shipment_id = None
            label_url = None
            for shipment_ids in result.get('data').get('ids'):
                shipment_id = shipment_ids.get('id')
                _logger.warning(F'shipment_id {shipment_id}')

            # get shipment info
            if shipment_id:
                multi_shipment_ids = []
                pickings.x_aa_mp_shipping_id = shipment_id
                shipment_info = myparcel_request.get_shipping(shipment_id)
                if 'postnl' in delivery_type:
                    shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                    if shipment_info['data']['shipments'][0]['secondary_shipments']:
                        multi_shipment_ids.append(int(shipment_id))
                        for secondary_shipment in shipment_info['data']['shipments'][0]['secondary_shipments']:
                            multi_shipment_ids.append(secondary_shipment['id'])
                            secondary_shipment_price = secondary_shipment['price']['amount'] / 100
                            shipment_price += secondary_shipment_price

                else:
                    shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                    shipment_status = shipment_info['data']['shipments'][0]['status']
                attachments = []
                if pickings.carrier_id.x_aa_mp_direct_label:
                    # get label
                    attachments = self.base_myparcel_get_label(pickings, shipment_id, myparcel_request)

                    _logger.warning(F'multi_shipment_ids {multi_shipment_ids}')
                    # get tracking code
                    if len(multi_shipment_ids) > 0:
                        tracking_code = self.base_myparcel_get_tracking_link(pickings, multi_shipment_ids,
                                                                             myparcel_request, attachments)
                    else:
                        tracking_code = self.base_myparcel_get_tracking_link(pickings, shipment_id, myparcel_request,
                                                                             attachments)

                    res = res + [{
                        'exact_price': shipment_price,
                        'tracking_number': tracking_code
                    }]
                else:
                    res = res + [{
                        'exact_price': False,
                        'tracking_number': False
                    }]

        elif pickings.x_aa_mp_shipping_id:
            multi_shipment_ids = []
            shipment_id = pickings.x_aa_mp_shipping_id
            shipment_info = myparcel_request.get_shipping(shipment_id)
            if 'postnl' in delivery_type:
                shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                if shipment_info['data']['shipments'][0]['secondary_shipments']:
                    multi_shipment_ids.append(int(shipment_id))
                    for secondary_shipment in shipment_info['data']['shipments'][0]['secondary_shipments']:
                        multi_shipment_ids.append(secondary_shipment['id'])
                        secondary_shipment_price = secondary_shipment['price']['amount'] / 100
                        shipment_price += secondary_shipment_price
            else:
                shipment_price = shipment_info['data']['shipments'][0]['price']['amount'] / 100
                shipment_status = shipment_info['data']['shipments'][0]['status']

            # get label
            attachments = self.base_myparcel_get_label(pickings, shipment_id, myparcel_request)

            _logger.warning(F'multi_shipment_ids {multi_shipment_ids} and shipment_id is {shipment_id}')

            # get tracking link
            if len(multi_shipment_ids) > 0:
                tracking_code = self.base_myparcel_get_tracking_link(pickings, multi_shipment_ids, myparcel_request,
                                                                     attachments)
            else:
                tracking_code = self.base_myparcel_get_tracking_link(pickings, shipment_id, myparcel_request,
                                                                     attachments)

            res = res + [{
                'exact_price': shipment_price,
                'tracking_number': tracking_code
            }]

        return res

    def base_myparcel_get_label(self, picking, shipment_id=None, myparcel_request=None):
        if shipment_id and myparcel_request:
            shipment_label = myparcel_request.get_label(shipment_id, self.x_aa_mp_label_size,
                                                        self._get_label_position_code(self.x_aa_mp_label_position))
            if shipment_label != 'Error':
                _logger.info(shipment_label)
                label_end_url = shipment_label['data']['pdfs']['url']
                label_url = f'https://api.myparcel.nl{label_end_url}'
                if picking:
                    picking.x_aa_mp_label_url = str(label_url)
                label_content = myparcel_request.download_file(label_url)
                attachments = [('LabelMyParcel.pdf', label_content)]

                return attachments
        else:
            if picking.x_aa_mp_shipping_id:
                res = []
                myparcel_request = self.get_myparcel_request(carrier_id=self, module_version=self.get_module_version())
                shipment_label = myparcel_request.get_label(picking.x_aa_mp_shipping_id,
                                                            picking.carrier_id.x_aa_mp_label_size,
                                                            picking.carrier_id._get_label_position_code(
                                                                picking.carrier_id.x_aa_mp_label_position))
                if shipment_label != 'Error':
                    _logger.info(shipment_label)
                    label_end_url = shipment_label['data']['pdfs']['url']
                    label_url = f'https://api.myparcel.nl{label_end_url}'
                    if picking:
                        picking.x_aa_mp_label_url = str(label_url)
                    label_content = myparcel_request.download_file(label_url)
                    attachments = [('LabelMyParcel.pdf', label_content)]

                    # get tracking link
                    tracking_code = self.base_myparcel_get_tracking_link(picking, picking.x_aa_mp_shipping_id,
                                                                         myparcel_request, attachments)

                    res = res + [{
                        'exact_price': False,
                        'tracking_number': tracking_code
                    }]

                return res

    @staticmethod
    def get_myparcel_base_tracking_url():
        return MYPARCEL_BASE_TRACK_TRACE_URL

    def base_myparcel_get_tracking_link(self, picking, shipment_id=None, myparcel_request=None, attachments=None):
        # TODO: Add other track and trace retrieving methods for the other carriers
        if 'postnl' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                if not isinstance(shipment_id, list):
                    track_trace = myparcel_request.track_trace(shipment_id)
                    track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']
                    _logger.warning(F'track_trace_link {track_trace_link}')
                    if track_trace_link:
                        parsed_url = urlparse(track_trace_link)
                        query_params = parse_qs(parsed_url.query)
                        tracking_code = query_params.get('B', [None])[0]
                        _logger.warning(F'tracking_code {tracking_code}')
                    else:
                        tracking_code = 'No tracking code found'

                    logmessage = _("Shipment created into MyParcel<br/>"
                                   "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                                   tracking_numbers=track_trace_link)
                    picking.message_post(body=logmessage, attachments=attachments)
                    return tracking_code
                else:
                    all_tracking_codes = 'No tracking code found'
                    for secondary_shipment in shipment_id:
                        track_trace = myparcel_request.track_trace(secondary_shipment)
                        track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']
                        if track_trace_link and secondary_shipment == shipment_id[0]:
                            parsed_url = urlparse(track_trace_link)
                            query_params = parse_qs(parsed_url.query)
                            tracking_code = query_params.get('B', [None])[0]
                            _logger.warning(F'tracking_code {tracking_code}')
                            all_tracking_codes = str(tracking_code)
                        elif track_trace_link and all_tracking_codes:
                            parsed_url = urlparse(track_trace_link)
                            query_params = parse_qs(parsed_url.query)
                            tracking_code = query_params.get('B', [None])[0]
                            _logger.warning(F'tracking_code {tracking_code}')
                            all_tracking_codes = all_tracking_codes + ' / ' + str(tracking_code)

                        logmessage = _("Shipment created into MyParcel<br/>"
                                       "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                                       tracking_numbers=track_trace_link)
                        picking.message_post(body=logmessage, attachments=attachments)
                    _logger.warning(F'all_tracking_codes {all_tracking_codes}')
                    return all_tracking_codes

        elif 'dhl' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                track_trace = myparcel_request.track_trace(shipment_id)
                track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']

                if track_trace_link:
                    split_link = track_trace_link.split('/')
                    tracking_code = split_link[-2]
                    _logger.warning(F'tracking_code {tracking_code}')
                else:
                    tracking_code = 'No tracking code found'

                logmessage = _("Shipment created into MyParcel<br/>"
                               "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                               tracking_numbers=track_trace_link)
                picking.message_post(body=logmessage, attachments=attachments)
                return tracking_code
        elif 'ups' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                track_trace = myparcel_request.track_trace(shipment_id)
                track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']

                if track_trace_link:
                    parsed_url = urlparse(track_trace_link)
                    query_params = parse_qs(parsed_url.query)
                    tracking_code = query_params.get('trackNums', [None])[0]
                    _logger.warning(F'tracking_code {tracking_code}')
                else:
                    tracking_code = 'No tracking code found'

                logmessage = _("Shipment created into MyParcel<br/>"
                               "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                               tracking_numbers=track_trace_link)
                picking.message_post(body=logmessage, attachments=attachments)
                return tracking_code
        elif 'dpd' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                track_trace = myparcel_request.track_trace(shipment_id)
                track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']
                if track_trace_link:
                    parsed_url = urlparse(track_trace_link)
                    query_params = parse_qs(parsed_url.query)
                    tracking_code = query_params.get('parcelNumber', [None])[0]
                    _logger.warning(F'tracking_code {tracking_code}')
                else:
                    tracking_code = 'No tracking code found'

                logmessage = _("Shipment created into MyParcel<br/>"
                               "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                               tracking_numbers=track_trace_link)
                picking.message_post(body=logmessage, attachments=attachments)
                return tracking_code
        elif 'gls' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                track_trace = myparcel_request.track_trace(shipment_id)
                track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']
                _logger.warning(F'track_trace_link {track_trace_link}')
                if track_trace_link:
                    parsed_url = urlparse(track_trace_link)
                    query_params = parse_qs(parsed_url.query)
                    tracking_code = query_params.get('parcelNumber', [None])[0]
                    _logger.warning(F'tracking_code {tracking_code}')
                else:
                    tracking_code = 'No tracking code found'

                logmessage = _("Shipment created into MyParcel<br/>"
                               "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                               tracking_numbers=track_trace_link)
                picking.message_post(body=logmessage, attachments=attachments)
                return tracking_code
        elif 'bpost' in picking.carrier_id.delivery_type:
            if shipment_id and myparcel_request:
                track_trace = myparcel_request.track_trace(shipment_id)
                track_trace_link = track_trace['data']['tracktraces'][0]['link_tracktrace']
                _logger.warning(F'track_trace_link {track_trace_link}')
                if track_trace_link:
                    parsed_url = urlparse(track_trace_link)
                    fragment_params = parse_qs(parsed_url.fragment)
                    _logger.warning(F'parsed_url {parsed_url}')
                    _logger.warning(F'fragment_params {fragment_params}')
                    tracking_code = fragment_params.get('/search?itemCode', [None])[0]
                    _logger.warning(F'tracking_code {tracking_code}')
                else:
                    tracking_code = 'No tracking code found'

                logmessage = _("Shipment created into MyParcel<br/>"
                               "<b>Tracking Links:</b> %(tracking_numbers)s<br/>",
                               tracking_numbers=track_trace_link)
                picking.message_post(body=logmessage, attachments=attachments)
                return tracking_code
        return

    def base_myparcel_cancel_shipment(self, picking):
        if picking.x_aa_mp_shipping_id:
            _logger.warning(F'delete shipment {picking.x_aa_mp_shipping_id}')
            myparcel_request = self.get_myparcel_request(carrier_id=self, module_version=self.get_module_version())
            result = myparcel_request.delete_shipment(picking.x_aa_mp_shipping_id)
            _logger.warning(F'delete shipment {result}')
        else:
            ValidationError(_('No MyParcel shipment ID found for this picking.'))
        return

    def base_myparcel_get_default_custom_package_code(self):
        return 'Custom Package Code'
