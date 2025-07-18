# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from odoo import fields, models


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(selection_add=[('myparcel_dhl_fy', 'MyParcel DHL For You'), ('myparcel_dhl_connect', 'MyParcel DHL Parcel Connect'), ('myparcel_dhl_europlus', 'MyParcel DHL Europlus'), ('myparcel_postnl', 'MyParcel Post NL')])
