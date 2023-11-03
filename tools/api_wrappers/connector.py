from wsimple.api import Wsimple
from tools.misc.credentials import Credentials
import time
import json
from databases.paths import Tokens
from selenium import webdriver
from selenium.webdriver.common.by import By

time_til_refresh = 3500


def get_otp():
    return input("Enter otpnumber: \n>>>")


class WealthSimpleConnector(Wsimple):

    def __init__(self, runs):
        # Credentials
        wcreds = Credentials.get_credentials(app_name='WealthSimple')

        # self.__init__ = Wsimple(wcreds[0], wcreds[1], otp_callback=get_otp)
        tokens_list = get_token_from_website(wcreds)
        tokens_dict = [{'Authorization': tokens_list[0]}, {'refresh_token': tokens_list[1]}]

        with open('C:\\Users\\hyacinthe\\Desktop\\Investment\\databases\\tokens.json', 'w') as f:
            # json.dump(self.__init__.box.tokens, f)
            json.dump(tokens_dict, f)
            f.close()

        print(f'Tokens created. Here are your tokens : {tokens_dict}')

        time.sleep(time_til_refresh)
        for run in range(int(runs)):
            new_tokens_list = get_token_from_website(wcreds)
            new_tokens_dict = [{'Authorization': new_tokens_list[0]}, {'refresh_token': new_tokens_list[1]}]

            with open('C:\\Users\\hyacinthe\\Desktop\\Investment\\databases\\tokens.json', 'w') as f:
                json.dump(new_tokens_dict, f)
                f.close()

            print(f'Tokens refreshed for the {run} time. Here are your new tokens : {new_tokens_dict}')
            time.sleep(time_til_refresh)

        print('TimeOut')

    def load_tokens(self):
        f = open(Tokens, 'r')
        return json.load(f)


def get_token_from_website(wcreds):
    driver = webdriver.Chrome()

    # Setting a delay so that we can see the browser window
    driver.get('https://my.wealthsimple.com/app/login?locale=en-ca')

    # -------------------------------------------------------------------------------------
    # LOG IN ENTRIES SECTION
    # USERNAME ENTRY
    user_name = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/'
                  'div/div/div/div/ng-transclude/div/layout/div/main'
                  '/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/'
                  'login-form/span/div/div/div/div/div/div/div[2]/div[1]/div[1]/input'
    )
    user_name[0].send_keys(wcreds[0])

    # PASSWORD ENTRY
    password = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/'
                  'ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/'
                  'ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/'
                  'div/div/div/div/div[3]/div[1]/div[1]/input'
    )
    password[0].send_keys(wcreds[1])

    # LOG IN CLICK
    login_button = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/'
                  'ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/'
                  'ng-transclude/form/ws-micro-app-loader/login-form/span/div/div/'
                  'div/div/div/div/div[5]/button'
    )
    login_button[0].click()

    # -------------------------------------------------------------------------------------
    # RECOVERY CODE SECTION
    # getting recovery code
    with open(
            'C:\\Users\\hyacinthe\\Desktop\\Investment\\tools\\bookingbot\\recovery_code.txt',
            'r',
            encoding='utf-8'
    ) as f:
        recov_code = f.read()

    time.sleep(1)
    recov_button = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                  'div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/'
                  'login-two-factor-form/div/div/ws-micro-app-loader/two-factor-auth-details/'
                  'span/div/div/div/div/div/div[4]/button[1]'
    )
    recov_button[0].click()

    # RECOV CODE ENTRY
    recov_entry = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                  'layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/login-two-factor-form/'
                  'div/div/ws-micro-app-loader/two-factor-recovery-details/span/div/div/div/div/div[2]/'
                  'div[1]/div[1]/input'
    )
    recov_entry[0].send_keys(recov_code)

    recov_button2 = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                  'layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/login-two-factor-form/'
                  'div/div/ws-micro-app-loader/two-factor-recovery-details/span/div/div/div/div/div[3]/button'
    )
    recov_button2[0].click()

    # NEW RECOV CODE FETCH
    time.sleep(2)
    recov_recuperation = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/'
                  'ng-transclude/div/layout/div/main/login-wizard/wizard/div/div/'
                  'ng-transclude/form/login-two-factor-form/div/div/ws-micro-app-loader/'
                  'two-factor-recovery-success/span/div/div/div/div/div[2]/div[1]/div[1]/input'
    )
    # Enter password
    new_recov_code = recov_recuperation[0].get_attribute("value")

    with open(
            'C:\\Users\\hyacinthe\\Desktop\\Investment\\tools\\bookingbot\\recovery_code.txt',
            'w',
            encoding='utf-8'
    ) as f:
        f.write(new_recov_code)

    recov_button3 = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                  'div/layout/div/main/login-wizard/wizard/div/div/ng-transclude/form/'
                  'login-two-factor-form/div/div/ws-micro-app-loader/two-factor-recovery-success/'
                  'span/div/div/div/div/div[3]/button'
    )
    recov_button3[0].click()

    # Scrap the cookies to get the new token pair
    raw_tokens = [value['value'] for value in driver.get_cookies() if '_oauth' in value['name']][0]
    tokens = read_raw_tokens(raw_tokens)

    return tokens


def read_raw_tokens(tok):
    access_token_start = tok.find('%7B%22access_token%22%3A%22') + len('%7B%22access_token%22%3A%22')
    access_token_end = tok.find('%22%2C%22token_type%22%3A')
    access_token = tok[access_token_start:access_token_end]

    refresh_token_start = tok.find('%2C%22refresh_token%22%3A%22') + len('%2C%22refresh_token%22%3A%22')
    refresh_token_end = tok.find('%22%2C%22scope%22%3A%22')
    refresh_token = tok[refresh_token_start:refresh_token_end]

    return [access_token, refresh_token]


if __name__ == '__main__':
    WealthSimpleConnector(runs=10)
