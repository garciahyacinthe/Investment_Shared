from tools.portfolio.accounting_pnl import AccountingPnL


def compute_accounting_pnl():
    ob = AccountingPnL()
    ob.print()
    print('')


if __name__ == '__main__':
    compute_accounting_pnl()
