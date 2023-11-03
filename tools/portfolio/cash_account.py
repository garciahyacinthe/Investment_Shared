from tools.api_wrappers.wealthsimple import WealthSimple
from databases.paths import CashAccountPath

class CashAccount:

    def __init__(self):

        ws = WealthSimple()
        self.db_path = CashAccountPath
        self.transactions_df = ws.get_cash_account_df(path=self.db_path)

    def print(self):
        self.transactions_df.to_csv(self.db_path)
