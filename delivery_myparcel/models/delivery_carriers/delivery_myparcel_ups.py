# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields
from .delivery_myparcel_base import BaseProviderMyParcel


class ProviderMyparcelUPS(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_ups', 'MyParcel - UPS')
    ], ondelete={
        'myparcel_ups': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    def myparcel_ups_rate_shipment(self, order):
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order)

    def myparcel_ups_send_shipping(self, pickings):
        return BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=pickings)

    def myparcel_ups_get_tracking_link(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_tracking_link(self, picking=picking)

    def myparcel_ups_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_ups_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
