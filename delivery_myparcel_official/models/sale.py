# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, _
from odoo.exceptions import ValidationError
from datetime import date
import logging

_logger = logging.getLogger()


class SaleOrder(models.Model):
    _inherit = ['sale.order', 'myparcel.mixin']
    _name = 'sale.order'

    x_aa_mp_is_myparcel = fields.Boolean(string='Is MyParcel Carrier', related='carrier_id.x_aa_mp_is_myparcel')
    x_aa_mp_is_sendmyparcel = fields.Boolean(string='Is SendMyParcel Carrier',
                                             related='carrier_id.x_aa_mp_is_sendmyparcel')
    x_aa_mp_selected_carrier = fields.Selection(string='Carrier Type', related='carrier_id.delivery_type')

    x_aa_mp_insurance_pricelist_id = fields.Many2one('myparcel.insurance.price', string='Delivery Insurance Price')

    def get_delivery_date_for_myparcel_rate(self):
        if self.commitment_date and self.commitment_date.date() > date.today():
            delivery_date = '{date} {time}'.format(**{
                'date': self.commitment_date.date(),
                'time': self.commitment_date.time(),
            })
        elif self.expected_date and self.expected_date.date() > date.today():
            delivery_date = '{date} {time}'.format(**{
                'date': self.expected_date.date(),
                'time': self.expected_date.time(),
            })
        else:
            raise ValidationError(_("Please set a future delivery date for the order."))
        return delivery_date

    def set_delivery_line(self, carrier, amount):
        res = super().set_delivery_line(carrier, amount)
        if res:
            for order in self:
                values = carrier._get_myparcel_values(obj=carrier, target=order)
                order.write(values)
        return res
