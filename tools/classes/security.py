from databases.paths import SecuritiesPath
from tools.misc.database_misc import get_from_db, find_str_in_df
from tools.misc.dates_misc import to_datetime

class Security:
    """
    Finds in the db, with whatever identifier
    Fills up the object
    """

    def __init__(self, identifier):
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
            # fills our object
            self.__dict__.update(infos_dict)

            # light date rework
            if not str(self.active_since_ws) == 'nan' and self.active_since_ws is not None:
                self.active_since_ws = to_datetime(self.active_since_ws, 'WealthSimple')
            if not str(self.inactive_since_ws) == 'nan' and self.inactive_since_ws is not None:
                self.inactive_since_ws = to_datetime(self.inactive_since_ws, 'WealthSimple')

        else:
            print(f'Please load the security {identifier} in the db.')
            quit()


if __name__ == '__main__':
    Security('^BCBCLI')
    Security('UCO')
    Security('SCO')

