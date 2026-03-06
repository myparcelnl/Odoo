# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import models, fields, api


class ResCountry(models.Model):
    _inherit = 'res.country'

    x_aa_mp_is_european = fields.Boolean('Is European', compute='_compute_country_is_european', store=True)

    @api.depends('country_group_ids')
    def _compute_country_is_european(self):
        for rec in self:
            if not rec.country_group_ids:
                rec.x_aa_mp_is_european = False
                continue
            if not self.env.ref('base.europe', raise_if_not_found=False):
                rec.x_aa_mp_is_european = rec.code in ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR',
                                                       'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL',
                                                       'PT', 'RO', 'SE', 'SI', 'SK']
            else:
                rec.x_aa_mp_is_european = self.env.ref('base.europe').id in rec.country_group_ids.ids
