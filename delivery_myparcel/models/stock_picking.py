# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, _
import logging

_logger = logging.getLogger()


class StockPicking(models.Model):
    _inherit = ['stock.picking', 'myparcel.mixin']
    _name = 'stock.picking'

    currency_id = fields.Many2one('res.currency', related='sale_id.currency_id')
    x_aa_mp_label_url = fields.Char('Label URL', help='The URL of the label for the shipment.', readonly=True,
                                    copy=False)

    x_aa_mp_insurance_pricelist_id = fields.Many2one('myparcel.insurance.price', string='Delivery Insurance Price')

    def action_send_to_myparcel(self):
        if self.carrier_id:
            return self.carrier_id.send_shipping(pickings=self)
        return False

    def action_get_myparcel_label(self):
        self.ensure_one()
        if hasattr(self.carrier_id, '%s_get_label' % self.delivery_type):
            return getattr(self.carrier_id, '%s_get_label' % self.delivery_type)(self)

    def _set_delivery_package_type(self, batch_pack=False):
        """ This method returns an action allowing to set the package type and the shipping weight
        on the stock.quant.package.
        """
        self.ensure_one()
        view_id = self.env.ref('stock_delivery.choose_delivery_package_view_form').id
        context = dict(
            self.env.context,
            current_package_carrier_type=self.carrier_id.delivery_type,
            current_package_carrier_type_id=self.carrier_id.x_aa_mp_package_type_id.id,
            default_picking_id=self.id,
            batch_pack=batch_pack,
        )
        # As we pass the `delivery_type` ('fixed' or 'base_on_rule' by default) in a key who
        # correspond to the `package_carrier_type` ('none' to default), we make a conversion.
        # No need conversion for other carriers as the `delivery_type` and
        #`package_carrier_type` will be the same in these cases.
        if context['current_package_carrier_type'] in ['fixed', 'base_on_rule']:
            context['current_package_carrier_type'] = 'none'
        # Update the context 'default_package_type_id' passed from JS
        # to populate the scanned package type in the package wizard opened from the barcode.
        if self.env.context.get('default_package_type_id'):
            context['default_delivery_package_type_id'] = self.env.context.get('default_package_type_id')
        return {
            'name': _('Package Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'choose.delivery.package',
            'view_id': view_id,
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }