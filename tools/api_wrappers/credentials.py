import json

path_to_cred = 'C:\\Users\\hyacinthe\\'
class Credentials:
    def get_credentials(app_name: str):
        with open(path_to_cred + "Credentials.txt", 'r') as j:
            dict_from_txt = json.loads(j.read())
        return dict_from_txt[app_name]

if __name__=='__main__':
    mycreds = Credentials.get_credentials(app_name='WealthSimple')