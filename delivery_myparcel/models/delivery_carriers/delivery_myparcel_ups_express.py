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


class ProviderMyparcelUPSExpress(models.Model):
    _inherit = ['delivery.carrier', 'myparcel.mixin']
    _name = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('myparcel_ups_express', 'MyParcel - UPS Express Saver')
    ], ondelete={
        'myparcel_ups_express': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})
    })

    @api.onchange(
        'x_aa_mp_age_control',
        'x_aa_mp_signing',
        'x_aa_mp_only_receiver',
    )
    def myparcel_ups_check_option_combi(self, wizard_id=None):
        if self.delivery_type == 'myparcel_ups_express':
            a = 1
            # if wizard_id:
            #     if (wizard_id.x_aa_mp_receiving_code and wizard_id.x_aa_mp_age_control) or (
            #             wizard_id.x_aa_mp_receiving_code and wizard_id.x_aa_mp_signing) or (
            #             wizard_id.x_aa_mp_receiving_code and wizard_id.x_aa_mp_only_receiver):
            #         raise ValidationError(
            #             _('Receipt code can not be selected with any other option. Please unselect the other options.'))
            #     if wizard_id.x_aa_mp_receiving_code and not wizard_id.x_aa_mp_insurance:
            #         raise ValidationError(
            #             _('Receipt code can only be used with insurance. Please select an insurance option.'))
            # else:
            #     if (self.x_aa_mp_receiving_code and self.x_aa_mp_age_control) or (
            #             self.x_aa_mp_receiving_code and self.x_aa_mp_signing) or (
            #             self.x_aa_mp_receiving_code and self.x_aa_mp_only_receiver):
            #         raise ValidationError(
            #             _('Receipt code can not be selected with any other option. Please unselect the other options.'))
            #     if self.x_aa_mp_receiving_code and not self.x_aa_mp_insurance:
            #         raise ValidationError(
            #             _('Receipt code can only be used with insurance. Please select an insurance option.'))

    def _myparcel_ups_express_get_options(self, order):
        options = {
            "package_type": self._get_package_type(self),
            "delivery_type": self._get_delivery_code(self.delivery_type),
            "label_description": order.name,
            "weight": order.shipping_weight,
        }

        options.update(self.generate_custom_field_options(fields=[
            ("age_check", "x_aa_mp_age_control"),
            ("signature", "x_aa_mp_signing"),
            ("only_recipient", "x_aa_mp_only_receiver"),
            ("insurance", "x_aa_mp_insurance"),
            ("insurance_price", "x_aa_mp_insurance_pricelist_id"),
        ], order=order, carrier=self))
        return options

    def myparcel_ups_express_rate_shipment(self, order):
        options = self._myparcel_ups_express_get_options(order)
        return BaseProviderMyParcel.base_myparcel_rate_shipment(self, order=order, options=options,
                                                                delivery_type=self.delivery_type)

    def myparcel_ups_express_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            options = self._myparcel_ups_express_get_options(picking)
            res = BaseProviderMyParcel.base_myparcel_send_shipping(self, pickings=picking, options=options,
                                                                   delivery_type=self.delivery_type)
        return res

    def myparcel_ups_express_get_label(self, picking):
        return BaseProviderMyParcel.base_myparcel_get_label(self, picking=picking)

    def myparcel_ups_express_get_tracking_link(self, picking):
        track_trace_base = BaseProviderMyParcel.get_myparcel_base_tracking_url()
        url = f'{track_trace_base}/{picking.carrier_tracking_ref}/{picking.partner_id.zip}/{picking.partner_id.country_id.code}'
        return url

    def myparcel_ups_express_cancel_shipment(self, picking):
        return BaseProviderMyParcel.base_myparcel_cancel_shipment(self, picking=picking)

    def _myparcel_ups_express_get_default_custom_package_code(self):
        return BaseProviderMyParcel.base_myparcel_get_default_custom_package_code(self)
