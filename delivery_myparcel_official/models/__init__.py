# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from . import stock_package_type
from . import res_country
from . import myparcel_mixin
from . import myparcel_insurance_price
from .delivery_carriers import delivery_myparcel_base
from .delivery_carriers import delivery_myparcel_postnl
from .delivery_carriers import delivery_myparcel_ups_standard
from .delivery_carriers import delivery_myparcel_ups_express
from .delivery_carriers import delivery_myparcel_dpd
from .delivery_carriers import delivery_myparcel_bpost
from .delivery_carriers import delivery_myparcel_dhl_fy
from .delivery_carriers import delivery_myparcel_dhl_connect
from .delivery_carriers import delivery_myparcel_dhl_europlus
# from .delivery_carriers import delivery_myparcel_gls
from . import stock_picking
from . import stock_move
from . import myparcel_request
from . import sale
