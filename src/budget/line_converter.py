

def in_and_out(input_file:str, output_file: str):
    output = []
    row = []
    with open(input_file, "rt", encoding="utf-8") as i:
        lines = i.readlines()
        for line in lines:
            d = line.split(",")
            account, t_date, amount, balance, category, desc, memo, notes = line.split(",")
            row.append(f"{t_date},{amount},{category}, {desc}")
            output.append(row)

        print(output)



if __name__ == '__main__':
    in_and_out("/Users/Paul/Downloads/checking_20200914.csv", "/Users/Paul/Downloads/checking_20200914_fixed.csv")
