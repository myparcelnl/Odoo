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
    - DHL Parcel Connect
    - PostNL
    - DPD
    - Bpost
    - UPS Standard
    - UPS Express Saver
    
    Currently Integrated (SendMyParcel):
    
    """,
    'category': 'Inventory/Delivery',
    'version': '0.4.0',
    'author': 'Aardug, MyParcel',
    'website': 'https://www.myparcel.nl/',
    'support': 'helpdesk@aardug.eu',
    'depends': ['stock_delivery', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/product_product.xml',
        'data/delivery_data/delivery_data_dhl_fy.xml',
        'data/delivery_data/delivery_data_dhl_connect.xml',
        'data/delivery_data/delivery_data_dhl_europlus.xml',
        'data/delivery_data/delivery_data_postnl.xml',
        'data/delivery_data/delivery_data_dpd.xml',
        'data/delivery_data/delivery_data_bpost.xml',
        'data/delivery_data/delivery_data_ups_standard.xml',
        'data/delivery_data/delivery_data_ups_express.xml',
        # 'data/delivery_data/delivery_data_gls.xml',
        'wizard/choose_delivery_carrier.xml',
        'wizard/choose_delivery_package_views.xml',
        'views/carrier_views/delivery_carrier_views.xml',
        'views/carrier_views/delivery_carrier_postnl_views.xml',
        'views/carrier_views/delivery_carrier_dhlfy_views.xml',
        'views/carrier_views/delivery_carrier_dhl_connect_views.xml',
        'views/carrier_views/delivery_carrier_dhl_europlus_views.xml',
        'views/carrier_views/delivery_carrier_dpd_views.xml',
        'views/carrier_views/delivery_carrier_bpost_views.xml',
        'views/carrier_views/delivery_carrier_ups_standard_views.xml',
        'views/carrier_views/delivery_carrier_ups_express_views.xml',
        # 'views/carrier_views/delivery_carrier_gls_views.xml',
        'views/stock_picking_views.xml',
        'views/sale_order_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
