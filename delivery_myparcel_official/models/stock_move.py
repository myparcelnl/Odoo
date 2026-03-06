# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################
from odoo import models, fields


class StockMove(models.Model):
    _inherit = ['stock.move', 'myparcel.mixin']
    _name = 'stock.move'

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        values = self.sale_line_id.order_id._get_myparcel_values(obj=self.sale_line_id.order_id, target=self.picking_id)
        vals.update(values)
        return vals
