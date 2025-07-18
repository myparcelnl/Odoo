# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class MyparcelInsurancePrice(models.Model):
    _name = 'myparcel.insurance.price'
    _description = 'MyParcel Insurance Price'

    carrier_id = fields.Many2one(comodel_name='delivery.carrier')
    delivery_type = fields.Selection(related='carrier_id.delivery_type')
    sale_id = fields.Many2one('sale.order')
    picking_id = fields.Many2one('stock.picking')

    currency_id = fields.Many2one('res.currency', related='carrier_id.currency_id')

    name = fields.Char('Name', compute='_compute_name', store=True)

    x_aa_mp_insurance_selection = fields.Selection(
        selection=lambda self: self.env['myparcel.mixin']._fields['x_aa_mp_insurance_amount'].selection,
        string='Insurance Amount',
        required=True,
    )

    price = fields.Monetary(
        currency_field='currency_id',
        required=True,
    )

    _sql_constraints = [
        (
            'unique_item_by_carrier', 'UNIQUE(name, carrier_id)',
            'All amounts must be unique!')
    ]

    @api.depends('x_aa_mp_insurance_selection')
    def _compute_name(self):
        for record in self:
            record.name = dict(self._fields['x_aa_mp_insurance_selection']._description_selection(self.env)).get(record.x_aa_mp_insurance_selection)
