from tools.portfolio.positions import Positions

def load_positions():
    pos = Positions()
    if pos.position_dict:
        print(
            f'You are long {str(int(pos.position_dict["quantity"]))} units of '
            f'{pos.position_dict["security_symbol"]}'
            f' at {str(float(pos.position_dict["price"]))} USD.'
            f' for a total of {str(int(pos.position_dict["amount"]))} USD.'
        )

    pos.print()

    return pos.position_dict

if __name__=='__main__':
    p = load_positions()


