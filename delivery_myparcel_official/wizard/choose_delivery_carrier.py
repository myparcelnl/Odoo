# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger()


class ChooseDeliveryCarrier(models.TransientModel):
    _inherit = ['choose.delivery.carrier', 'myparcel.mixin']
    _name = 'choose.delivery.carrier'

    x_aa_mp_is_myparcel = fields.Boolean(related='carrier_id.x_aa_mp_is_myparcel')
    x_aa_mp_is_sendmyparcel = fields.Boolean(related='carrier_id.x_aa_mp_is_sendmyparcel')

    carrier_message = fields.Text(compute='_compute_carrier_message')

    x_aa_mp_insurance_pricelist_id = fields.Many2one('myparcel.insurance.price', string='Price')

    country_code = fields.Char(related='order_id.partner_shipping_id.country_id.code', string='Country Code',
                               readonly=True)
    european_country_code = fields.Boolean(related='order_id.partner_shipping_id.country_id.x_aa_mp_is_european',
                                       string='Is European Country', readonly=True)

    commitment_date = fields.Datetime(related='order_id.commitment_date', string='Delivery Date', readonly=False)

    @api.onchange('carrier_id')
    def _onchange_carrier_id(self):
        if self.order_id and self.order_id.carrier_id and self.order_id.carrier_id == self.carrier_id:
            self.write({
                'x_aa_mp_age_control': self.order_id.x_aa_mp_age_control,
                'x_aa_mp_signing': self.order_id.x_aa_mp_signing,
                'x_aa_mp_only_receiver': self.order_id.x_aa_mp_only_receiver,
                'x_aa_mp_receiving_code': self.order_id.x_aa_mp_receiving_code,
                'x_aa_mp_direct_return': self.order_id.x_aa_mp_direct_return,
                'x_aa_mp_large_package': self.order_id.x_aa_mp_large_package,
                'x_aa_mp_hide_sender': self.order_id.x_aa_mp_hide_sender,
                'x_aa_mp_insurance': self.order_id.x_aa_mp_insurance,
                'x_aa_mp_insurance_pricelist_id': self.order_id.x_aa_mp_insurance_pricelist_id,
                'x_aa_mp_allow_sameday_delivery': self.order_id.x_aa_mp_allow_sameday_delivery,
            })
        elif self.carrier_id and (self.carrier_id.x_aa_mp_is_myparcel or self.carrier_id.x_aa_mp_is_sendmyparcel):
            self.write({
                'x_aa_mp_age_control': self.carrier_id.x_aa_mp_age_control,
                'x_aa_mp_signing': self.carrier_id.x_aa_mp_signing,
                'x_aa_mp_only_receiver': self.carrier_id.x_aa_mp_only_receiver,
                'x_aa_mp_receiving_code': self.carrier_id.x_aa_mp_receiving_code,
                'x_aa_mp_direct_return': self.carrier_id.x_aa_mp_direct_return,
                'x_aa_mp_large_package': self.carrier_id.x_aa_mp_large_package,
                'x_aa_mp_hide_sender': self.carrier_id.x_aa_mp_hide_sender,
                'x_aa_mp_insurance': False,
                'x_aa_mp_insurance_pricelist_id': False,
                'x_aa_mp_allow_sameday_delivery': self.carrier_id.x_aa_mp_allow_sameday_delivery,
            })
        else:
            self.write({
                'x_aa_mp_age_control': False,
                'x_aa_mp_signing': False,
                'x_aa_mp_only_receiver': False,
                'x_aa_mp_receiving_code': False,
                'x_aa_mp_direct_return': False,
                'x_aa_mp_large_package': False,
                'x_aa_mp_insurance': False,
                'x_aa_mp_insurance_pricelist_id': False,
                'x_aa_mp_hide_sender': False,
                'x_aa_mp_allow_sameday_delivery': False,
            })
        return super()._onchange_carrier_id()

    @api.onchange(
        'x_aa_mp_age_control',
        'x_aa_mp_signing',
        'x_aa_mp_only_receiver',
        'x_aa_mp_receiving_code',
        'x_aa_mp_large_package',
        'x_aa_mp_direct_return',
        'x_aa_mp_hide_sender',
        'x_aa_mp_insurance',
        'x_aa_mp_insurance_pricelist_id'
    )
    def check_carrier_combi(self):
        if self.order_id and self.order_id.carrier_id and self.order_id.carrier_id == self.carrier_id:
            if hasattr(self.carrier_id, '%s_check_option_combi' % self.carrier_id.delivery_type):
                getattr(self.carrier_id, '%s_check_option_combi' % self.carrier_id.delivery_type)(wizard_id=self)
        elif self.carrier_id and (self.carrier_id.x_aa_mp_is_myparcel or self.carrier_id.x_aa_mp_is_sendmyparcel):
            # self.carrier_id.check_option_combi(wizard_id=self)
            if hasattr(self.carrier_id, '%s_check_option_combi' % self.carrier_id.delivery_type):
                getattr(self.carrier_id, '%s_check_option_combi' % self.carrier_id.delivery_type)(wizard_id=self)

    @api.depends('carrier_id')
    def _compute_carrier_message(self):
        self.carrier_message = ''
        if self.carrier_id:
            if self.carrier_id.delivery_type:
                if 'dhl_fy' in self.carrier_id.delivery_type:
                    if self.carrier_id.x_aa_mp_allow_sameday_delivery:
                        self.carrier_message = _('Same day delivery is available for this delivery.')
                    else:
                        self.carrier_message = _('Same day delivery is not available for this delivery.')
                if 'dhl_europlus' in self.carrier_id.delivery_type:
                    self.carrier_message = _('Signature is always required for Europlus deliveries.')
                if 'gls' in self.carrier_id.delivery_type:
                    self.carrier_message = _('Signature is always required outside the Netherlands for GLS deliveries.')

    def _get_delivery_rate(self):
        self_context = self.with_context(x_aa_mp_age_control=self.x_aa_mp_age_control,
                                         x_aa_mp_signing=self.x_aa_mp_signing,
                                         x_aa_mp_only_receiver=self.x_aa_mp_only_receiver,
                                         x_aa_mp_receiving_code=self.x_aa_mp_receiving_code,
                                         x_aa_mp_large_package=self.x_aa_mp_large_package,
                                         x_aa_mp_direct_return=self.x_aa_mp_direct_return,
                                         x_aa_mp_hide_sender=self.x_aa_mp_hide_sender,
                                         x_aa_mp_insurance=self.x_aa_mp_insurance,
                                         x_aa_mp_insurance_pricelist_id=self.x_aa_mp_insurance_pricelist_id,
                                         x_aa_mp_allow_sameday_delivery=self.x_aa_mp_allow_sameday_delivery)
        return super(ChooseDeliveryCarrier, self_context)._get_delivery_rate()

    def button_confirm(self):
        if not self.x_aa_mp_insurance:
            self.x_aa_mp_insurance_pricelist_id = False
        res = super().button_confirm()
        values = self._get_myparcel_values(obj=self, target=self.order_id)
        self.order_id.write(values)
        return res
