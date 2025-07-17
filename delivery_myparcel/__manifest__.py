# -*- coding: utf-8 -*-
##############################################################################
#                                                                            #
# Part of Aardug. (Website: www.aardug.nl).                                  #
# See LICENSE file for full copyright and licensing details.                 #
#                                                                            #
##############################################################################

{
    'name': 'MyParcel Shipping',
    'description': """
    Shipping integration with MyParcel platform.
    Note: this is a BETA version. Not all features are fully implemented yet.
    
    Currently Integrated (MyParcel):
    - DHL For You
    - DHL Europlus
    
    Currently Integrated (SendMyParcel):
    
    """,
    'category': 'Inventory/Delivery',
    'version': '0.1.2',
    'author': 'Aardug, MyParcel',
    'website': 'https://www.myparcel.nl/',
    'support': 'helpdesk@aardug.eu',
    'depends': ['stock_delivery', 'mail'],
    'data': [
        'data/product_product.xml',
        'wizard/choose_delivery_carrier.xml',
        'views/carrier_views/delivery_carrier_views.xml',
        # 'views/carrier_views/delivery_carrier_postnl_views.xml',
        'views/carrier_views/delivery_carrier_dhlfy_views.xml',
        'views/carrier_views/delivery_carrier_dhl_europlus_views.xml',
        # 'views/carrier_views/delivery_carrier_dpd_views.xml',
        # 'views/carrier_views/delivery_carrier_ups_views.xml',
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
