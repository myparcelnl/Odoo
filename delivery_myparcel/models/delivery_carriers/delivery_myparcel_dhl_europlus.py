# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, api

from .delivery_myparcel_base import BaseProviderMyParcel
import logging

_logger = logging.getLogger()


class ProviderMyparcelDHLEuroplus(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_dhl_europlus', 'MyParcel - DHL Europlus')
    ], ondelete={
        'myparcel_dhl_europlus': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    x_aa_mp_signing = fields.Boolean(default=True)

    def _myparcel_dhl_europlus_get_options(self, order):
        options = {
            "package_type": self._get_package_type(),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
            "saturday_delivery": 0,
        }

        # There is a situation where the order doesnt have this as a carrier yet, but also there is no context.
        # For example when we are coming from a webshop order.
        # In that case we use the default values from the carrier.
        options.update(self.generate_custom_field_options(fields=[
            ("signature", "x_aa_mp_signing"),
            ("hide_sender", "x_aa_mp_hide_sender"),
        ], order=order, carrier=self))
        return options

    def myparcel_dhl_europlus_rate_shipment(self, order):
        options = self._myparcel_dhl_europlus_get_options(order)
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_dhl_europlus_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_dhl_europlus_get_options(picking)
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_dhl_europlus_get_label(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_label(self, picking=picking)

    def myparcel_dhl_europlus_get_tracking_link(self, picking):
        url = f"https://my.dhlparcel.nl/home/tracktrace/{picking.carrier_tracking_ref}/{picking.partner_id.zip}"
        return url

    def myparcel_dhl_europlus_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def myparcel_dhl_europlus_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
