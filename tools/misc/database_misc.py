import os
import pandas as pd

def generate_folder(path):
    """
    Python prog to check if directory exists and creates it
    """
    # path = path_name + f'\{directory_name}'
    isExist= os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print(f"The new directory is created for {path}.")

def check_if_db(csv_path):
    """
    Python prog to check if directory exists and creates it
    """
    # path = path_name + f'\{directory_name}'
    return os.path.exists(csv_path)


def get_from_db(path, index_name):

    df = pd.read_csv(path, index_col=index_name)

    return df

def merge_new_and_old_db(new_df, old_df, index_name):

    raw_df = pd.concat([old_df, new_df]).reset_index()
    # rework of type for constats series
    if index_name == 'timestamp':
        filter_df = pd.to_datetime(raw_df[index_name], format='mixed').drop_duplicates()
    else:
        filter_df = raw_df[index_name].drop_duplicates()

    concat_df = raw_df.reset_index().loc[
        raw_df.index.isin(list(filter_df.index))].set_index(index_name).drop(columns='index')

    return concat_df

def refresh_db(path, df):
    df.to_csv(path)
    # print('Refreshed ' + path)

def find_str_in_df(df, searched_string):

    df = df.reset_index()

    # Search for the string 'al' in all columns
    mask = df.applymap(lambda x: search_string(x, searched_string))

    # Filter the DataFrame based on the mask
    filtered_df = df.loc[mask.any(axis=1)]

    return filtered_df

def search_string(s, search):
    return search.lower() == str(s).lower()

