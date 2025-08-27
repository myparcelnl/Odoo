# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, api, _
from .delivery_myparcel_base import BaseProviderMyParcel
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger()


class ProviderMyparcelGLS(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_gls', 'MyParcel - GLS')
    ], ondelete={
        'myparcel_gls': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    @api.onchange(
        'x_aa_mp_signing',
    )
    def myparcel_gls_check_option_combi(self, wizard_id=None):
        if self.delivery_type == 'myparcel_gls':
            if wizard_id:
                _logger.warning(F'wizard_id.order_id.partner_id.country_id.code {wizard_id.order_id.partner_id.country_id.code}')
                _logger.warning(F'wizard_id.x_aa_mp_signing {wizard_id.x_aa_mp_signing}')
                if not wizard_id.x_aa_mp_signing and wizard_id.order_id.partner_id.country_id.code != 'NL':
                    raise ValidationError(
                        _('Signing required outside the Netherlands. Please select the signing option.'))
    def _myparcel_gls_get_options(self, order):
        options = {
            "package_type": self._get_package_type(self),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
            "weight": order.shipping_weight,
        }

        options.update(self.generate_custom_field_options(fields=[
            ("signature", "x_aa_mp_signing"),
        ], order=order, carrier=self))
        return options

    def myparcel_gls_rate_shipment(self, order):
        options = self._myparcel_gls_get_options(order)
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_gls_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_gls_get_options(picking)
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_gls_get_tracking_link(self, picking):
        track_trace_base = BaseProviderMyParcel.get_myparcel_base_tracking_url()
        url = f'{track_trace_base}/{picking.carrier_tracking_ref}/{picking.partner_id.zip}/{picking.partner_id.country_id.code}'
        return url

    def myparcel_gls_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_gls_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
