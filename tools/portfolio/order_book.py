from tools.api_wrappers.wealthsimple import WealthSimple
from databases.paths import OrderBookPath
from tools.misc.database_misc import generate_folder, get_from_db, merge_new_and_old_db, refresh_db, check_if_db

class OrderBook:

    def __init__(self):

        ws = WealthSimple()
        self.db_path = OrderBookPath
        self.order_book_df = ws.get_ob_df(path=self.db_path)

    def print(self):
        # loads df and merges with new one

        old_db = get_from_db(self.db_path, index_name='unique_indicator')
        new_db = merge_new_and_old_db(new_df=self.order_book_df, old_df=old_db, index_name='unique_indicator')

        # saves to csv
        refresh_db(df=new_db, path=self.db_path)








