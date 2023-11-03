from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from tools.misc.credentials import Credentials

order_type_locations = {
    'market': (780, 580),
    'limit': (780, 600),
    'stop_limit': (780, 620)
}

# Credentials
wcreds = Credentials.get_credentials(app_name='WealthSimple')


def book(booking_dict):
    # Setup chrome driver
    # service = ChromeService(executable_path=ChromeDriverManager().install())
    # driver = webdriver.Chrome(service=service)
    driver = webdriver.Chrome()
    # Setting a delay so that we can see the browser window
    driver.get('https://my.wealthsimple.com/app/login?locale=en-ca')

    # -------------------------------------------------------------------------------------
    # LOG IN ENTRIES SECTION
    # USERNAME ENTRY
    time.sleep(1)
    user_name = driver.find_elements(
        By.XPATH,
        # '/html/body/div[1]/ws-card-loading-indicator/'
        #           'div/div/div/div/ng-transclude/div/layout/div/main'
        #           '/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader/'
        #           'login-form/span/div/div/div/div/div/div[2]/div[1]/div[1]/input'

        '/html/body/div[1]/ws-card-loading-indicator/'
        'div/div/div/div/ng-transclude/div/layout/div/main'
        '/login-wizard/wizard/div/div/ng-transclude/form/ws-micro-app-loader'
        '/login-form/span/div/div/div/div/div/div/div[2]/div[1]/div[1]/input'

    )
    # time.sleep(30)
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
                  'span/div/div/div/div/div[4]/button[1]'
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

    # -------------------------------------------------------------------------------------
    # BOOKING SECTION
    # Stocks, ETFs, Cryptos button
    time.sleep(1)
    stocketfcrypto_button = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                  'div/layout/div/main/ws-product-switcher-breather-component/ws-micro-app-loader/'
                  'product-switcher-breather/span/div/div/div/div/div[3]/div/button'
    )
    stocketfcrypto_button[0].click()

    time.sleep(1)
    ticker_entry = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                  'div/layout/div/header-component/header/div/ws-micro-app-loader/page-header/span/'
                  'div/div[1]/div/div/div[1]/div[1]/div[2]/input'
    )
    # TICKER
    ticker_entry[0].send_keys(booking_dict['Ticker'])

    time.sleep(1)
    list_ticker_button = driver.find_elements(
        By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/'
                  'layout/div/header-component/header/div/ws-micro-app-loader/page-header/span/div/div[1]'
                  '/div/div/div[2]/button[1]'
    )
    list_ticker_button[0].click()

    # Cash available on TFSA
    # trade_acc_button = driver.find_elements(
    #     By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/div[2]/div/div[2]/div/div[2]/div[1]/div/div[1]/select'
    # )
    # trade_acc_button[0].click()
    time.sleep(1)
    list_trade_acc = driver.find_elements(
        By.XPATH,
        '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/div[2]/div/div[2]/div/div[2]/div[1]/div/div[1]/select/option[2]'
    )
    cash_start_position = list_trade_acc[0].accessible_name.find('$')
    cash_end_position = list_trade_acc[0].accessible_name.find(' USD')
    cash_available = float(
        list_trade_acc[0].accessible_name[cash_start_position + 1:cash_end_position].replace(',', '')
    )

    # TODO choose between buy and sell
    # ORDERS
    if booking_dict['OrderType'] == 'market':
        # Quantity computing
        if booking_dict['CashToInvest'] == 'all':
            # We apply a discount >5% (margin for market orders)
            quantity = (cash_available * 0.949) / booking_dict['Price']
        else:
            # We apply a discount >5% (margin for market orders)
            quantity = round((booking_dict['CashToInvest'] * 0.949) / booking_dict['Price'], 2)

        # safety
        quantity = 1

        # Effective booking
        qty_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                      'div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/'
                      'span/span/div[2]/div/div[2]/div/div[2]/div[3]/div/div[1]/div[1]/div[1]/input'
        )
        # Quantity entry
        qty_entry[0].send_keys(quantity)

        # Book click
        book_button = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                      'div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/'
                      'span/div[2]/div/div[2]/div/div[2]/button'
        )
        book_button[0].click()

        # Tips
        time.sleep(1)
        tips_button1 = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div[2]/button'
        )
        tips_button1[0].click()

        time.sleep(1)
        tips_button2 = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div[2]/button[1]'
        )
        tips_button2[0].click()

        # Confirm
        confirm_button = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div/div[4]/div[2]/button[1]'
        )
        # confirm_button[0].click()

    if booking_dict['OrderType'] == 'limit':
        # Quantity computing
        if booking_dict['CashToInvest'] == 'all':
            # We apply a discount >5% (margin for market orders)
            quantity = (cash_available * 0.949) / booking_dict['Price']
        else:
            # We apply a discount >5% (margin for market orders)
            quantity = round((booking_dict['CashToInvest'] * 0.949) / booking_dict['Price'], 2)

        # safety
        quantity = 1

        # Choose stop limit
        ordertype_button = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                      'div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/'
                      'span/span/div[2]/div/div[2]/div/div[2]/div[2]/div/div[1]/select/option[3]'
        )
        ordertype_button[0].click()

        # Effective booking
        time.sleep(1)
        # Limit Price entry
        limit_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                      'div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/'
                      'div[2]/div/div[2]/div/div[2]/div[3]/div/div[1]/div[1]/input'
        )
        limit_entry[0].send_keys(quantity)

        # Quantity entry
        qty_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/'
                      'layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/div[2]/'
                      'div/div[2]/div/div[2]/div[4]/div/div[1]/div[1]/div[1]/input'
        )
        qty_entry[0].send_keys(quantity)

        # Book click
        book_button = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                      'div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/'
                      'span/div[2]/div/div[2]/div/div[2]/button'
        )
        book_button[0].click()

        # Confirm steps
        time.sleep(1)
        conf_button1 = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div/div[2]/button[1]'
        )
        conf_button1[0].click()

        time.sleep(1)
        # tick box
        conf_button2 = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div/label'
        )
        conf_button2[0].click()

        # confirm
        conf_button3 = driver.find_elements(
            By.XPATH, '/html/body/span/div/div/div[2]/div/div[4]/div[2]/button[1]'
        )
        # conf_button3[0].click()

    if booking_dict['OrderType'] == 'stop_limit':
        # Quantity computing
        if booking_dict['CashToInvest'] == 'all':
            # We apply a discount >5% (margin for market orders)
            quantity = (cash_available * 0.949) / booking_dict['Price']
        else:
            # We apply a discount >5% (margin for market orders)
            quantity = round((booking_dict['CashToInvest'] * 0.949) / booking_dict['Price'], 2)

        # Choose limit
        ordertype_button = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                      'div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/'
                      'div[2]/div/div[2]/div/div[2]/div[2]/div/div[1]/select/option[4]'
        )
        ordertype_button[0].click()

        # Effective booking
        # Stop Price entry
        stop_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/'
                      'div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/'
                      'div[2]/div/div[2]/div/div[2]/div[3]/div/div[1]/div[1]/input'
        )
        stop_entry[0].send_keys(booking_dict['StopPrice'])

        # Limit Price entry
        limit_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/'
                      'layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/div[2]/'
                      'div/div[2]/div/div[2]/div[4]/div/div[1]/div[1]/input'
        )
        limit_entry[0].send_keys(booking_dict['Price'])

        # Quantity entry
        qty_entry = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/div/div/'
                      'layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/span/div[2]/'
                      'div/div[2]/div/div[2]/div[5]/div/div[1]/div[1]/div[1]/input'
        )
        qty_entry[0].send_keys(quantity)

        # Book click
        book_button = driver.find_elements(
            By.XPATH, '/html/body/div[1]/ws-card-loading-indicator/div/div/div/div/ng-transclude/'
                      'div/div/layout/div/main/ws-trade-component/div/ws-micro-app-loader/routes/span/'
                      'span/div[2]/div/div[2]/div/div[2]/button'
        )
        book_button[0].click()

        # Confirm
        # confirm_button = driver.find_elements(
        #     By.XPATH, '/html/body/span/div/div/div[2]/div/div[4]/div[2]/button[1]'
        # )
        # confirm_button[0].click()
        # TODO finish here if needed


if __name__ == '__main__':
    # signal = {
    #     'security_id': 'SCO',
    #     'way': 'sell',
    #     'order_type': 'market',
    #     'quantity': 1,
    #     'stop_price': 40,
    #     'limit_price': 40,
    # }
    # book(
    #   signal
    # )
    get_token_from_website()
    # book({
    #     'Ticker': 'SCO',
    #     'CashToInvest': 100,
    #     'OrderType': 'limit',
    #     'Price': 19.37,
    #     'StopPrice': 19.37
    # })
