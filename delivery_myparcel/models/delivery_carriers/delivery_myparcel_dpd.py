# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields
from .delivery_myparcel_base import BaseProviderMyParcel


class ProviderMyparcelDPD(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_dpd', 'MyParcel - DPD')
    ], ondelete={
        'myparcel_dpd': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    def myparcel_dpd_rate_shipment(self, order):
        options = {
            "package_type": self._get_package_type(),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
        }
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_dpd_send_shipping(self, pickings):
        return BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=pickings)

    def myparcel_dpd_get_tracking_link(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_tracking_link(self, picking=picking)

    def myparcel_dpd_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_dpd_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
