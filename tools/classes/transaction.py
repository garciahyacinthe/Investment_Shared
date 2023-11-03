from tools.misc.classes_misc import iterable
from tools.misc.dates_misc import to_datetime

from databases.fees import fee_rate
from databases.mappings import transaction_exclusion_mapping, cash_asset_mapping, accounts

@iterable
class Transaction():
    def __init__(self, app_name, app_object):
        if app_name == "WealthSimple":

            self.unique_indicator = app_object.id
            self.type = app_object.id[0:app_object.id.find('-')]

            if self.type not in transaction_exclusion_mapping:

                # -----------------------------------------
                if cash_asset_mapping[self.type] == 'cash':

                    # -----------------------------------
                    if self.type == 'custodian_account_activity':

                        self.asset = 'currency'

                        # cad
                        if app_object.net_cash['currency'] == 'CAD':
                            self.cad = app_object.net_cash['amount']
                        else:
                            self.cad = 0

                        # usd
                        if app_object.net_cash['currency'] == 'USD':
                            self.usd = app_object.net_cash['amount']
                        else:
                            self.usd = 0

                        self.fx_rate = 1

                        if self.fx_rate != 1:
                            self.fees_cad = fee_rate * float(self.cad)
                            self.fees_usd = fee_rate * float(self.usd)
                        else:
                            self.fees_cad = 0
                            self.fees_usd = 0

                        self.from_account = 'Custodian'
                        self.to_account = accounts[app_object.account_id]
                        self.date = to_datetime(app_object.effective_date, 'WealthSimple')

                    #-----------------------------------
                    if self.type == 'internal_transfer':
                        self.asset = 'currency'
                        #cad
                        self.cad = [
                            app_object.assets[x].quantity
                            for x in range(len(app_object.assets))
                            if app_object.assets[x].security_id == 'sec-c-cad'
                        ]
                        if self.cad:
                            self.cad = self.cad[0]
                            # Way
                            if 'CAD' in accounts[app_object.source_account_id]: self.cad = -float(self.cad)
                        else:
                            self.cad = 0

                        #usd
                        self.usd = [
                            app_object.assets[x].quantity
                            for x in range(len(app_object.assets))
                            if app_object.assets[x].security_id == 'sec-c-usd'
                        ]

                        if self.usd:
                            self.usd = self.usd[0]
                            # Way
                            if 'USD' in accounts[app_object.source_account_id]: self.usd = -float(self.usd)
                        else:
                            self.usd = 0

                        self.fx_rate = app_object.fx_rate

                        if self.fx_rate != 1:
                            self.fees_cad = fee_rate * float(self.cad)
                            self.fees_usd = fee_rate * float(self.usd)
                        else:
                            self.fees_cad = 0
                            self.fees_usd = 0

                        self.from_account = accounts[app_object.source_account_id]
                        self.to_account = accounts[app_object.destination_account_id]
                        self.date = to_datetime(app_object.post_dated, 'WealthSimple')
                        self.unique_indicator = app_object.id

                    # -----------------------------------
                    if self.type == 'funding_intent':

                        self.asset = 'currency'
                        # cad
                        if app_object.currency == 'CAD':
                            self.cad = app_object.amount
                        else:
                            self.cad = 0

                        # usd
                        if app_object.currency == 'USD':
                            self.usd = app_object.amount
                        else:
                            self.usd = 0

                        self.fx_rate = 1

                        if self.fx_rate != 1:
                            self.fees_cad = fee_rate * float(self.cad)
                            self.fees_usd = fee_rate * float(self.usd)
                        else:
                            self.fees_cad = 0
                            self.fees_usd = 0

                        self.from_account = accounts[app_object.metadata.source_financial_institution]
                        self.to_account = accounts[app_object.account_id]
                        self.date = to_datetime(app_object.completed_at, 'WealthSimple')

                    # -----------------------------------
                    if self.type == 'payment':

                        self.asset = 'currency'
                        # cad
                        if app_object.currency == 'CAD':
                            self.cad = app_object.total_amount.amount
                        else:
                            self.cad = 0

                        # usd
                        if app_object.currency == 'USD':
                            self.usd = app_object.total_amount.amount
                        else:
                            self.usd = 0

                        self.fx_rate = 1

                        if self.fx_rate != 1:
                            self.fees_cad = fee_rate * float(self.cad)
                            self.fees_usd = fee_rate * float(self.usd)
                        else:
                            self.fees_cad = 0
                            self.fees_usd = 0

                        self.from_account = accounts[app_object.account_id]
                        self.to_account = None
                        self.date = to_datetime(app_object.start_at, 'WealthSimple')

                # ---------------------------------------------
                if cash_asset_mapping[self.type] == 'physical':

                    # -----------------------------------
                    # if self.type == 'asset_movement_request':

                            # self.asset = None
                            # self.cad = 0
                            # self.usd = 0
                            # self.fx_rate = 1
                            # self.fees_cad = 0
                            # self.fees_usd = 0
                            # self.from_account = accounts[app_object.account_id]
                            # self.to_account = None
                            # self.date = to_datetime(app_object.completed_at, 'WealthSimple')

                    # -----------------------------------
                    if self.type == 'order':
                        if app_object.status not in ['cancelled', 'submitted']:

                            self.asset = app_object.security_name

                            # cad
                            if app_object.account_currency == 'CAD':
                                self.cad = app_object.account_value['amount']
                            else:
                                self.cad = 0

                            # usd
                            if app_object.account_currency == 'USD':
                                self.usd = app_object.account_value['amount']
                            else:
                                self.usd = 0

                            self.fx_rate = app_object.fill_fx_rate

                            if self.fx_rate != 1:
                                self.fees_cad = fee_rate * float(self.cad)
                                self.fees_usd = fee_rate * float(self.usd)
                            else:
                                self.fees_cad = 0
                                self.fees_usd = 0

                            if app_object.order_type == 'buy_quantity':
                                self.from_account = accounts[app_object.account_id]
                                self.to_account = None
                                self.usd = -self.usd
                                self.cad = -self.cad

                            if app_object.order_type == 'sell_quantity':
                                self.from_account = accounts[app_object.account_id]
                                self.to_account = None

                            self.date = to_datetime(app_object.filled_at, 'WealthSimple')
        else:
            self.result=None