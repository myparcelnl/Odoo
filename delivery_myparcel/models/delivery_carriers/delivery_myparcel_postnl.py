# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, _
from .delivery_myparcel_base import BaseProviderMyParcel


class ProviderMyparcelPostNL(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_postnl', 'MyParcel - PostNL')
    ], ondelete={
        'myparcel_postnl': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    def _myparcel_postnl_get_options(self, order):
        options = {
            "package_type": self._get_package_type(),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
        }

        options.update(self.generate_custom_field_options(fields=[
            ("age_check", "x_aa_mp_age_control"),
            ("signature", "x_aa_mp_signing"),
            ("only_recipient", "x_aa_mp_only_receiver"),
            ("return", "x_aa_mp_direct_return"),
            ("large_format", "x_aa_mp_large_package"),
            ("hide_sender", "x_aa_mp_hide_sender"),
        ], order=order, carrier=self))
        return options

    def myparcel_postnl_rate_shipment(self, order):
        options = self._myparcel_postnl_get_options(order)
        delivery_date = order.get_delivery_date_for_myparcel_rate()
        options.update({'delivery_date': delivery_date})
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_postnl_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_postnl_get_options(picking)
            delivery_date = '{date} {time}'.format(**{
                'date': picking.scheduled_date.date(),
                'time': picking.scheduled_date.time(),
            })
            options.update({'delivery_date': delivery_date})
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_postnl_get_tracking_link(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_tracking_link(self, picking=picking)

    def myparcel_postnl_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_postnl_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
