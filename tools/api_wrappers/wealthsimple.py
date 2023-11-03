from wsimple.api import Wsimple
from tools.misc.credentials import Credentials
from tools.misc.database_misc import get_from_db, merge_new_and_old_db
from tools.misc.objects_helper import partial_flat
from tools.classes.order import Order
from tools.classes.transaction import Transaction
from tools.classes.quote import Quote
from tools.classes.security import Security
from databases.paths import Tokens
import pandas as pd
import json

class WealthSimple(Wsimple):

    def __init__(self):
        # Credentials
        wcreds = Credentials.get_credentials(app_name='WealthSimple')

        # Connector
        self.__init__ = Wsimple(wcreds[0], wcreds[1], oauth_mode=True, internally_manage_tokens=False)

        # Accounts
        self.accounts = {
            f'account_{box.account_type}_{box.base_currency}_id': box.id
            for box in self.__init__.get_accounts(tokens=self.load_tokens()).results
        }

    def load_tokens(self):
        f = open(Tokens, 'r')
        return json.load(f)

    def get_ob_df(self, path):

        orders_list_df = [
            pd.DataFrame(Order(app_name='WealthSimple', app_object=order))
            for order in self.__init__.get_activities(tokens=self.load_tokens()).results
            if order.object == 'order'
        ]
        clean_orders_list = [df.set_index(0) for df in orders_list_df if not df.empty]
        new_orders_df = pd.concat(clean_orders_list, axis=1).T.set_index('unique_indicator', drop=True)

        # merge with old db
        old_orders_df = get_from_db(path, 'unique_indicator')
        orders_df = merge_new_and_old_db(
            new_df=new_orders_df, old_df=old_orders_df, index_name='unique_indicator'
        )

        return orders_df

    def get_cash_account_df(self, path):

        transaction_list_df = [
            pd.DataFrame(Transaction(app_name='WealthSimple', app_object=transaction)).set_index(0)
            for acc_id in self.accounts.values()
            for transaction in self.__init__.get_activities(tokens=self.load_tokens(), limit=99, account_id=acc_id).results
        ]
        transaction_df = pd.concat(transaction_list_df, axis=1).T.set_index('unique_indicator', drop=True)

        # merge with old db
        old_cash_account = get_from_db(path, 'unique_indicator')
        full_cash_account = merge_new_and_old_db(
            new_df=transaction_df, old_df=old_cash_account, index_name='unique_indicator'
        )

        # Remove nan
        full_cash_account = full_cash_account.loc[full_cash_account['asset'].notna()]

        return full_cash_account

    def get_quotes_ws(self, sec_id):

        quotes = self.__init__.find_securities_by_id_historical(
            sec_id=sec_id, tokens=self.load_tokens(), time="1y"
        ).results

        quotes_list = [
            pd.DataFrame(Quote(app_name='WealthSimple', app_object=quote)).set_index(0)
            for quote in quotes
        ]

        quotes_df = pd.concat(quotes_list, axis=1).T
        quotes_df.to_csv(f'C:\\Users\\hyacinthe\\Desktop\\Investment\\databases\\Quotes_{sec_id}.csv')
        return quotes_df

    def get_security_infos_by_ticker(self, ticker):

        sec_infos = self.__init__.find_securities(
            tokens=self.load_tokens(),
            ticker=ticker
        )

        if sec_infos is not None: sec_infos = partial_flat(sec_infos, 'stock')

        return sec_infos

    def get_security_infos_by_id(self, id):

        sec_infos = self.__init__.find_securities_by_id(
            tokens=self.load_tokens(),
            sec_id=id
        )

        if sec_infos is not None: sec_infos = partial_flat(sec_infos, 'stock')

        return sec_infos

def get_otp():
    return input("Enter otpnumber: \n>>>")

if __name__ == '__main__':
    ws = WealthSimple()
    ob = ws.get_ob_df()
    print('')


# # AccountManagement
# account_cad = ws.get_accounts().results[0]
# account_usd = ws.get_accounts().results[1]
# account_data_cad = ws.get_historical_portfolio_data(tokens=ws.box.access_token, time='all', account_id=account_cad.id)
# account_data_usd = ws.get_historical_portfolio_data(tokens=ws.box.access_token, time='all', account_id=account_usd.id)
#
# # Positions
# pose = ws.get_positions()
#
# # Order Book
# orders = ws.get_orders(account_id=account_usd)
# orders = ws.get_orders(account_id=account_cad)
# activities = ws.get_activities()
#
# print(ws.get_market_hours(exchange="NYSE"))
# BUY:
#
# {
# 	"account_id": <ACCT_ID>,
# 	"quantity": 1,
# 	"security_id": <SID>,
# 	"order_type": "buy_quantity",
# 	"order_sub_type": "market",
# 	"time_in_force": "day",
# 	"limit_price": 0.195
# }
# SELL:
#
# {
# 	"account_id": <ACCT_ID>,
# 	"quantity": 1,
# 	"security_id": <SID>,
# 	"order_type": "sell_quantity",
# 	"order_sub_type": "market",
# 	"time_in_force": "day"
# }
# print('')

