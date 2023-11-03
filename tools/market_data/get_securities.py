import pandas as pd
from databases.paths import SecuritiesPath
from tools.api_wrappers.wealthsimple import WealthSimple
from databases.mappings import ws_security, yf_security
from tools.api_wrappers.yahoofinance import get_security_infos_by_ticker
from tools.misc.database_misc import get_from_db, merge_new_and_old_db, refresh_db, find_str_in_df
from tools.misc.objects_helper import mapping_to_dict
from tools.misc.dates_misc import to_datetime


class Securities:
    """
    Transcodify from the db or fetches it from data sources
    Fills up the object
    Feeds the db
    """

    def __init__(self, identifier):
        to_print = False
        infos_dict = {}

        # ------------------
        # Database intent to fetch
        infos_df = get_from_db(SecuritiesPath, 'ticker')
        # looks for the identifier and if located, returns the index
        infos_df_filtered = find_str_in_df(infos_df, identifier)
        if not infos_df_filtered.empty:
            infos_dict = infos_df_filtered.T.to_dict()
            infos_dict = infos_dict[list(infos_dict.keys())[0]]

        # ------------------
        # API calls if no db row
        if not infos_dict:
            to_print = True

            # built the dict
            yf_dict = load_secu_from_yf(identifier)
            infos_dict.update(yf_dict)

            ws_dict = load_secu_from_ws(identifier)
            infos_dict.update(ws_dict)

            # gives yf another try with ws ticker
            if yf_dict['ticker'] is None:
                yf_dict = load_secu_from_yf(ws_dict['ticker'])
                infos_dict.update(yf_dict)

            # no data fetched
            if not infos_dict:
                print('needs to load from another source')

        # ------------------
        # fills our object
        self.__dict__.update(infos_dict)

        # light date rework
        if not str(self.inactive_since_ws) == 'nan' and self.active_since_ws is not None:
            self.active_since_ws = to_datetime(self.active_since_ws, 'WealthSimple')
        if not str(self.inactive_since_ws) == 'nan' and self.inactive_since_ws is not None:
            self.inactive_since_ws = to_datetime(self.inactive_since_ws, 'WealthSimple')

        # ------------------
        # add the row in db
        if to_print == True:
            new_infos_df = pd.DataFrame.from_dict(infos_dict, orient='index').T.set_index('ticker')
            # if file
            if infos_df.empty:
                refresh_db(
                    df=new_infos_df,
                    path=SecuritiesPath
                )
            else:
                refresh_db(
                    df=merge_new_and_old_db(new_df=new_infos_df, old_df=infos_df, index_name='ticker'),
                    path=SecuritiesPath
                )


def load_secu_from_ws(identifier_ws):

    ws = WealthSimple()
    secu_dict = mapping_to_dict(
        app_object=ws.get_security_infos_by_ticker(ticker=identifier_ws),
        mapping=ws_security
    )

    # tries with the security id
    if not secu_dict:
        secu_dict = mapping_to_dict(
            app_object=ws.get_security_infos_by_id(id=identifier_ws),
            mapping=ws_security
        )

    # fill with None
    if not secu_dict:
        secu_dict = {key: None for key in ws_security.keys()}
        secu_dict['WealthSimple'] = False
    else:
        secu_dict['WealthSimple'] = True


    return secu_dict


def load_secu_from_yf(identifier_yf):

    secu_dict = mapping_to_dict(
        app_object=get_security_infos_by_ticker(ticker=identifier_yf),
        mapping=yf_security
    )

    # fill with None
    if not secu_dict:
        secu_dict = {key: None for key in yf_security.keys()}
        secu_dict['YahooFinance'] = False
    else:
        secu_dict['YahooFinance'] = True

    return secu_dict


if __name__ == '__main__':
    Securities('^BCBCLI')
    Securities('UCO')
    Securities('SCO')

