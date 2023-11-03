cash_asset_mapping = {
    'internal_transfer': 'cash',
    'funding_intent': 'cash',
    'custodian_account_activity': 'cash',
    'payment': 'cash',
    'order': 'physical',
    'asset_movement_request': 'physical',
}

transaction_exclusion_mapping = [
    'asset_movement',
    # 'asset_movement_request',
]

accounts = {
    'tfsa-_SeXdnnorA': 'Compte_CAD_WS',
    'tfsa-5r1sdefy': 'Compte_USD_WS',
    'RBC (CA000003)': 'Compte_CAD_RBC'
}

ws_security = {
    'ticker': 'symbol',
    'security_name_ws': 'name',
    'security_id_ws': 'id',
    'security_type_ws': 'security_type',
    'currency_ws': 'currency',
    'active_since_ws': 'active_date',
    'inactive_since_ws': 'inactive_date'
}

yf_security = {
    'ticker': 'ticker',
    'security_name_yf': 'longName',
    'security_id_yf': 'uuid',
    'security_type_yf': 'quoteType',
    'currency_yf': 'currency',
}

yf_quotes_type_vs_interval = {
    'daily': '1d',
    'intra_1m': '1m',
    'intra_2m': '2m',
}