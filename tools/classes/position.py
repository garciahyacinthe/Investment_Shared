from tools.misc.classes_misc import iterable
import numpy as np
import pandas as pd

@iterable
class Position():
    def __init__(self, ob_df):

        position_df = pd.pivot_table(
            data=ob_df,
            columns='security_symbol',
            values=['quantity', 'amount'],
            aggfunc={
                'quantity': np.sum,
                # 'amount': np.sum,
            }
        ).T
        position_df = position_df[position_df['quantity'] != 0]

        # looks for last open order if any, to get its execution price
        if not position_df.empty:
            ob = ob_df.loc[ob_df['security_symbol'] == position_df.index[0]]
            order = ob['execution_timestamp'].sort_values(ascending=False).index[0]
            position_df['price'] = ob.loc[order]['price']
            position_df['amount'] = ob.loc[order]['amount']
            position_df['quantity'] = ob.loc[order]['quantity']

        self.position_df = position_df


