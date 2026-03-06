
MYPARCEL_DELIVERY_TYPES = [
    'myparcel_postnl',
    'myparcel_ups_standard',
    'myparcel_ups_express',
    'myparcel_dpd',
    'myparcel_dhl_fy',
    'myparcel_dhl_connect',
    'myparcel_dhl_europlus',
    'myparcel_gls',
    # TODO: Complete this list
]

SENDMYPARCEL_DELIVERY_TYPES = [
    'myparcel_postnl',
    'myparcel_dpd',
    # 'myparcel_dhl_fy',
    # 'myparcel_dhl_connect',
    # 'myparcel_dhl_europlus',
    'myparcel_bpost',
    # TODO: Complete this list
]

MYPARCEL_CARRIER_CODES = {
    'myparcel_postnl': 1,
    'myparcel_bpost': 2,
    'myparcel_dpd': 4,
    'myparcel_dhl_fy': 9,
    'myparcel_dhl_connect': 10,
    'myparcel_dhl_europlus': 11,
    'myparcel_ups_standard': 12,
    'myparcel_ups_express': 13,
    'myparcel_gls': 14,
}

# TODO: Change these codes for delivery or pickup when available
MYPARCEL_DELIVERY_CODES = {
    'myparcel_postnl': 2,
    'myparcel_bpost': 2,
    'myparcel_dpd': 2,
    'myparcel_dhl_fy': 2,
    'myparcel_dhl_connect': 2,
    'myparcel_dhl_europlus': 2,
    'myparcel_ups_standard': 2,
    'myparcel_ups_express': 2,
    'myparcel_gls': 2,
}

MYPARCEL_LABEL_POSITIONS_CODES = {
    'top_left': 1,
    'top_right': 2,
    'bottom_left': 3,
    'bottom_right': 4,
}

MYPARCEL_BASE_TRACK_TRACE_URL = 'https://myparcel.me/track-trace'