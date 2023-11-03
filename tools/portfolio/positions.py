import pandas as pd

from tools.api_wrappers.wealthsimple import WealthSimple
from tools.misc.database_misc import get_from_db, merge_new_and_old_db
from tools.classes.position import Position
from databases.paths import OrderBookPath, PositionsPath

class Positions:

    def __init__(self):

        ws = WealthSimple()
        self.db_path = PositionsPath
        self.order_book_df = ws.get_ob_df(path=OrderBookPath)
        self.positions = Position(self.order_book_df).position_df
        if not self.positions.empty:
            self.position_dict = self.positions.reset_index().to_dict(orient='index')[0]
        else:
            self.position_dict = {}

    def print(self):
        self.positions.to_csv(self.db_path)








