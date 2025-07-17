# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields
import logging

_logger = logging.getLogger()


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'myparcel.mixin']
    _name = 'stock.picking'

    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id')
    x_aa_mp_label_url = fields.Char('Label URL', help='The URL of the label for the shipment.', readonly=True,
                                    copy=False)

    def action_send_to_myparcel(self):
        if self.carrier_id:
            return self.carrier_id.send_shipping(pickings=self)
        return False

    def action_get_myparcel_label(self):
        self.ensure_one()
        if hasattr(self.carrier_id, '%s_get_label' % self.delivery_type):
            return getattr(self.carrier_id, '%s_get_label' % self.delivery_type)(self)