from tools.api_wrappers.connector import WealthSimpleConnector

def wealthsimpleconnection():
    hours_to_run = input('Input the number of hours you want to stay connected to Wealthsimple: ')
    print('Connecting to Wealth Simple for ' + str(hours_to_run) + ' hours.')
    WealthSimpleConnector(hours_to_run)


