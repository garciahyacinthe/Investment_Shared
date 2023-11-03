from tools.misc.classes_misc import iterable

@iterable
class Order():
    def __init__(self, app_name, app_object):
        if app_name == "WealthSimple":
            if app_object.status not in ['cancelled', 'submitted']:

                self.unique_indicator = app_object.order_id
                self.security_name = app_object.security_name
                self.security_symbol = app_object.symbol
                self.security_id = app_object.security_id
                self.price = float(app_object.filled_net_value) / float(app_object.fill_quantity) / float(app_object.fill_fx_rate)
                if app_object.order_type == 'sell_quantity':
                    self.quantity = -float(app_object.fill_quantity)
                    self.amount = -float(app_object.filled_net_value)
                elif app_object.order_type == 'buy_quantity':
                        self.quantity = float(app_object.fill_quantity)
                        self.amount = float(app_object.filled_net_value)
                self.currency = app_object.market_currency
                self.fx_rate = float(app_object.fill_fx_rate)
                self.order_type = app_object.order_type
                self.order_sub_type = app_object.order_sub_type
                self.status = app_object.status
                self.submission_timestamp = app_object.submittedAtUtc
                self.execution_timestamp = app_object.perceived_filled_at
                self.account_id = app_object.account_id






