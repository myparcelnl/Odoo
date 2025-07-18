# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################
import odoo.release
from odoo import fields, models, _
from odoo.exceptions import ValidationError
import logging

from odoo.addons.delivery_myparcel.data.myparcel_static_data import MYPARCEL_CARRIER_CODES, MYPARCEL_DELIVERY_CODES, \
    MYPARCEL_LABEL_POSITIONS_CODES

_logger = logging.getLogger()


class MyParcelMixin(models.AbstractModel):
    _name = 'myparcel.mixin'
    _description = "MyParcel Mixin"

    # Order shipment ID
    x_aa_mp_shipping_id = fields.Char(string='MyParcel Shipment ID')

    # Carrier settings
    x_aa_mp_age_control = fields.Boolean(string='Age Verification (18+)', default=False)
    x_aa_mp_signing = fields.Boolean(string='Require Signature', default=False)
    x_aa_mp_only_receiver = fields.Boolean(string='Receiver Only', default=False)
    x_aa_mp_receiving_code = fields.Boolean(string='Receipt Code', default=False)
    x_aa_mp_large_package = fields.Boolean(string='Larger than 100x70x58 cm', default=False)
    x_aa_mp_direct_return = fields.Boolean(string='Direct Return', default=False)
    x_aa_mp_package_collection_carrier = fields.Boolean(string='Package Collect by Carrier',
                                                        default=False)
    x_aa_mp_hide_sender = fields.Boolean(string='Hide Sender', default=False)
    x_aa_mp_insurance = fields.Boolean(string='Activate Insurance', default=False)
    x_aa_mp_insurance_amount = fields.Selection(
        selection=[
            ('10000', '100'),
            ('25000', '250'),
            ('50000', '500'),
            ('100000', '1000'),
            ('150000', '1500'),
            ('200000', '2000'),
            ('250000', '2500'),
            ('300000', '3000'),
            ('350000', '3500'),
            ('400000', '4000'),
            ('450000', '4500'),
            ('500000', '5000'),
        ],
        string='Insured amount',
        copy=False,
    )
    x_aa_mp_home_delivery = fields.Boolean(string='Home delivery', default=False)
    x_aa_mp_allow_standard_delivery = fields.Boolean(string='Standard Delivery', default=False)
    x_aa_mp_standard_delivery_price = fields.Float(string='Standard Delivery Price')
    x_aa_mp_allow_sameday_delivery = fields.Boolean(string='Same-day Delivery', default=False)
    x_aa_mp_sameday_delivery_price = fields.Float(string='Same-day Delivery Price')
    x_aa_mp_allow_morning_delivery = fields.Boolean(string='Morning Delivery', default=False)
    x_aa_mp_morning_delivery_price = fields.Float(string='Morning Delivery Price')
    x_aa_mp_allow_evening_delivery = fields.Boolean(string='Evening Delivery', default=False)
    x_aa_mp_evening_delivery_price = fields.Float(string='Evening Delivery Price')
    x_aa_mp_allow_monday_delivery = fields.Boolean(string='Monday Delivery', default=False)
    x_aa_mp_monday_delivery_price = fields.Float(string='Monday Delivery Price')
    x_aa_mp_allow_saturday_delivery = fields.Boolean(string='Saturday Delivery', default=False)
    x_aa_mp_saturday_delivery_price = fields.Float(string='Saturday Delivery Price')

    # # Delivery time selection
    def _get_delivery_time_options(self):
        """Dynamically update the delivery time options based on the carrier's settings."""
        options = []
        if self:
            if self.x_aa_mp_allow_standard_delivery:
                options.append(('standard', 'Standaard Bezorging'))
            if self.x_aa_mp_allow_sameday_delivery:
                options.append(('sameday', 'Zelfde dag Bezorging'))
            if self.x_aa_mp_allow_morning_delivery:
                options.append(('morning', 'Ochtendbezorging'))
            if self.x_aa_mp_allow_evening_delivery:
                options.append(('evening', 'Avondbezorging'))
            if self.x_aa_mp_allow_monday_delivery:
                options.append(('monday', 'Maandagbezorging'))
            if self.x_aa_mp_allow_saturday_delivery:
                options.append(('saturday', 'Zaterdagbezorging'))
            return options
        else:
            return [('standard', 'Standaard Bezorging')]

    # Delivery time selection
    x_aa_mp_delivery_time = fields.Selection(
        selection=_get_delivery_time_options,
        string='Bezorgtijd',
        help='Selecteer de bezorgtijd op basis van de beschikbare opties voor de vervoerder.'
    )

    def _get_myparcel_values(self, obj, target):
        values = {}
        for field in self._fields:
            if field.startswith('x_aa_mp_'):
                if field == 'x_aa_mp_insurance_pricelist_id' and obj._name not in ('choose.delivery.carrier', 'sale.order', 'stock.picking'):
                    continue
                val = getattr(obj, field)
                if isinstance(val, models.Model):
                    val = val.id
                if hasattr(target, field):
                    values[field] = val
        return values

    def get_module_version(self):
        current_module = self.env['ir.module.module'].sudo().search([('name', '=', 'delivery_myparcel')],
                                                                    limit=1)
        current_version = current_module.installed_version if current_module else odoo.release.version
        return current_version

    @staticmethod
    def _get_carrier_code(delivery_type=False):
        if delivery_type in MYPARCEL_CARRIER_CODES:
            return MYPARCEL_CARRIER_CODES.get(delivery_type)
        else:
            raise ValidationError(_('Unrecognised carrier while getting carrier code.'))

    @staticmethod
    def _get_delivery_code(delivery_type=False):
        if delivery_type in MYPARCEL_DELIVERY_CODES:
            return MYPARCEL_DELIVERY_CODES.get(delivery_type)
        else:
            raise ValidationError(_('Unrecognised carrier while getting delivery code.'))

    @staticmethod
    def _get_label_position_code(label_position=False):
        if label_position in MYPARCEL_LABEL_POSITIONS_CODES:
            return MYPARCEL_LABEL_POSITIONS_CODES.get(label_position)
        else:
            raise ValidationError(_('Unrecognised label position while getting label position code.'))

    @staticmethod
    def _get_package_type(carrier=None):
        if carrier:
            package_type = int(carrier.x_aa_mp_package_type_id.shipper_package_code)
        else:
            package_type = 1
        _logger.warning(F'Package type is {package_type}')
        return package_type

    def generate_custom_field_options(self, fields=None, order=False, carrier=False):
        options = {}
        if not fields or (not order and not carrier):
            return options
        try:
            for option_key, context_key in fields:
                order_or_carrier = order if order and order.carrier_id == carrier else carrier
                if option_key == 'insurance_price' and options['insurance'] == 1:
                    options[option_key] = self.env.context.get(context_key, getattr(order_or_carrier, context_key, False)) if self.env.context.get(context_key, getattr(order_or_carrier, context_key, False)) else 0
                else:
                    options[option_key] = 1 if self.env.context.get(context_key, getattr(order_or_carrier, context_key, False)) else 0
        except:
            _logger.error("Error generating custom field options")
            return options

        return options
