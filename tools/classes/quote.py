from tools.misc.dates_misc import to_datetime
from tools.misc.classes_misc import iterable
from tools.classes.security import Security

@iterable
class Quote():

    def __init__(self, app_name, app_object, infos):

        if app_name == "WealthSimple":

            self.security_id = Security(identifier=app_object.security_id).ticker
            self.timestamp = to_datetime(app_object.date, 'WealthSimple')
            self.close = app_object.close
            self.price = app_object.adjusted_price
            self.volume = None

        if app_name == "YahooFinance":
            # we leverage on the fact that yahoo is sending us back a df, we just normalize it
            app_object['ticker'] = infos['ticker']
            app_object['interval'] = infos['interval']
            app_object.index.name = 'timestamp'
            self.reworked_df = app_object


