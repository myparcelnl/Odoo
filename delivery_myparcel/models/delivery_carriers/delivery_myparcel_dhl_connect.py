# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields
from .delivery_myparcel_base import BaseProviderMyParcel


class ProviderMyparcelDHLConnect(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_dhl_connect', 'MyParcel - DHL Parcel Connect')
    ], ondelete={
        'myparcel_dhl_connect': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    x_aa_mp_signing = fields.Boolean(string='Signature', default=True)

    def _myparcel_dhl_connect_get_options(self, order):
        options = {
            "package_type": self._get_package_type(self),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
            "weight": order.shipping_weight,
        }

        # There is a situation where the order doesnt have this as a carrier yet, but also there is no context.
        # For example when we are coming from a webshop order.
        # In that case we use the default values from the carrier.
        options.update(self.generate_custom_field_options(fields=[
            ("signature", "x_aa_mp_signing"),
            # ("return", "x_aa_mp_direct_return"),
            ("insurance", "x_aa_mp_insurance"),
            ("insurance_price", "x_aa_mp_insurance_pricelist_id"),
        ], order=order, carrier=self))
        return options

    def myparcel_dhl_connect_rate_shipment(self, order):
        options = self._myparcel_dhl_connect_get_options(order)
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_dhl_connect_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_dhl_connect_get_options(picking)
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_dhl_connect_get_label(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_label(self, picking=picking)

    def myparcel_dhl_connect_get_tracking_link(self, picking):
        track_trace_base = BaseProviderMyParcel.get_myparcel_base_tracking_url()
        url = f'{track_trace_base}/{picking.carrier_tracking_ref}/{picking.partner_id.zip}/{picking.partner_id.country_id.code}'
        # url = f"https://my.dhlparcel.nl/home/tracktrace/{picking.carrier_tracking_ref}/{picking.partner_id.zip}"
        return url

    def myparcel_dhl_connect_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_dhl_connect_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
