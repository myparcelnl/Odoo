# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields
from .delivery_myparcel_base import BaseProviderMyParcel
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger()


class ProviderMyparcelDPD(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_dpd', 'MyParcel - DPD')
    ], ondelete={
        'myparcel_dpd': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    x_aa_mp_email_send_with_shipment = fields.Boolean(string='Add Email to Shipment', default=True)

    def _myparcel_dpd_get_options(self, order):
        options = {
            "package_type": self._get_package_type(self),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
            "weight": order.shipping_weight,
        }

        # options.update(self.generate_custom_field_options(fields=[
        #     ("return", "x_aa_mp_direct_return"),
        # ], order=order, carrier=self))
        return options

    def myparcel_dpd_rate_shipment(self, order):
        options = self._myparcel_dpd_get_options(order)
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_dpd_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_dpd_get_options(picking)
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_dpd_get_tracking_link(self, picking):
        track_trace_base = BaseProviderMyParcel.get_myparcel_base_tracking_url()
        url = f'{track_trace_base}/{picking.carrier_tracking_ref}/{picking.partner_id.zip}/{picking.partner_id.country_id.code}'
        return url

    def myparcel_dpd_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_dpd_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
