# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

from . import stock_package_type
from . import myparcel_mixin
from .delivery_carriers import delivery_myparcel_base
# from .delivery_carriers import delivery_myparcel_postnl
# from .delivery_carriers import delivery_myparcel_ups
# from .delivery_carriers import delivery_myparcel_dpd
from .delivery_carriers import delivery_myparcel_dhl_fy
# from .delivery_carriers import delivery_myparcel_dhl_connect
from .delivery_carriers import delivery_myparcel_dhl_europlus
from . import stock_picking
from . import stock_move
from . import myparcel_request
from . import sale
