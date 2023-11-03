from tools.market_data.get_securities import Securities

def add_security_in_db(general_identifier):
    Securities(general_identifier)

if __name__== '__main__':
    add_security_in_db("sec-s-30c0a70434a7402db53b79a72688ef52")