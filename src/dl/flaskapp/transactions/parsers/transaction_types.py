from dateutil.parser import parse


class CapitalOneTransaction:
    def __init__(self, transaction):
        self.account = transaction['Card No.']
        self.date = parse(transaction['Posted Date'])
        self.year = self.date.year
        self.month = self.date.month
        self.day_of_month = self.date.day
        self.description = transaction['Description']
        self.category = transaction['Category']
        if transaction['Debit']:
            self.debit = float(transaction['Debit'])
        if transaction['Credit']:
            self.credit = float(transaction['Credit'])

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


class CMCUTransaction:
    debit_none_remap = {
        'AutoLoan': ['AUTO'],
        'Auto': ['Oil', 'Tire', 'Tint'],
        'Fuel': ['CONOCO', 'SUNOCO', 'Love'],
        'Credit Card': ['Capital One Card', 'CC'],
        'Utilities': ['CITY OF', 'PIEDMONT', 'Water', 'PNG', 'Duke'],
        'Cell Phone': ['Cell Phone'],
        'Fee': ['Simply Elite'],
        'PayPal': ['PAYPAL'],
        'Insurance': ['STATE FARM'],
        'Taxes': ['MECKLENBURG TAX', 'NC DEPT REVENUE'],
        'Health': ['PLANET FIT', 'MASSAGE ENVY', 'Radiology', 'Gastro', 'Surgical', 'Medical', 'Novant', 'Dr.', 'LCI'],
        'Investments': ['VANGUARD', 'TROWE'],
        'Misc Purchase': ['POS Withdrawal'],
        'Entertainment': ['Netflix', 'HULU'],
        'Wages': ['Deposit'],
        'Transfer To Checking': ['From Share'],
        'From Checking': ['Online Withdrawal']

    }

    def __init__(self, transaction):
        self.account = transaction['account']
        self.amount = self._normalize_amount(transaction['amount'])
        self.date = parse(transaction['date'])
        self.year = self.date.year
        self.balance = self._normalize_amount(transaction['balance'])
        self.description = transaction['description']
        self.memo = transaction['memo']
        self.category = self._recategorize(transaction['category'])
        self.deposit = False

    def _normalize_amount(self, amount):
        if amount:
            is_negative = '(' in amount
            stripped_amount = amount.strip('(').strip(')').strip('$')
            if is_negative:
                self.deposit = False
                return float(stripped_amount)
            else:
                self.deposit = True
                return float(stripped_amount)
        return None

    def _recategorize(self, category_in):
        if category_in in ['DebitNone', 'CreditNone', 'CreditTransfer']:
            for k, v in self.debit_none_remap.items():
                found_in_desc = any(kw.upper() in self.description.upper() for kw in v)
                found_in_memo = any(kw.upper() in self.memo.upper() for kw in v)
                if found_in_desc or found_in_memo:
                    return k
        else:
            return category_in
        return 'Misc'

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


class HealthData:
    def __init__(self, record):
        data_dict = record.attrib
        self.type = data_dict['type'][24:]
        self.unit = data_dict['unit']
        self.value = float(data_dict['value'])
        the_date = parse(data_dict['creationDate'])
        self.date = the_date.replace(hour=0, minute=0, second=0, microsecond=0)

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__


class WeatherData:
    def __init__(self, data_row):
        self.station_name = data_row['STATION_NAME']
        self.date = format(data_row['DATE'])
        self.dly_prcp_25pctl = self._evaluate(data_row['DLY-PRCP-25PCTL'])
        self.dly_snwd_25pctl = self._evaluate(data_row['DLY-SNWD-25PCTL'])
        self.dly_snow_25pctl = self._evaluate(data_row['DLY-SNOW-25PCTL'])
        self.dly_prcp_50pctl = self._evaluate(data_row['DLY-PRCP-50PCTL'])
        self.dly_snwd_50pctl = self._evaluate(data_row['DLY-SNWD-50PCTL'])
        self.dly_snow_50pctl = self._evaluate(data_row['DLY-SNOW-50PCTL'])
        self.dly_prcp_75pctl = self._evaluate(data_row['DLY-PRCP-75PCTL'])
        self.dly_snwd_75pctl = self._evaluate(data_row['DLY-SNWD-75PCTL'])
        self.dly_snow_75pctl = self._evaluate(data_row['DLY-SNOW-75PCTL'])
        self.mtd_prcp_normal = self._evaluate(data_row['MTD-PRCP-NORMAL'])
        self.mtd_snow_normal = self._evaluate(data_row['MTD-SNOW-NORMAL'])
        self.ytd_prcp_normal = self._evaluate(data_row['YTD-PRCP-NORMAL'])
        self.ytd_snow_normal = self._evaluate(data_row['YTD-SNOW-NORMAL'])
        self.dly_prcp_pctall_ge001hi = self._evaluate(data_row['DLY-PRCP-PCTALL-GE001HI'])
        self.dly_prcp_pctall_ge010hi = self._evaluate(data_row['DLY-PRCP-PCTALL-GE010HI'])
        self.dly_prcp_pctall_ge050hi = self._evaluate(data_row['DLY-PRCP-PCTALL-GE050HI'])
        self.dly_prcp_pctall_ge100hi = self._evaluate(data_row['DLY-PRCP-PCTALL-GE100HI'])
        self.dly_snwd_pctall_ge001wi = self._evaluate(data_row['DLY-SNWD-PCTALL-GE001WI'])
        self.dly_snwd_pctall_ge010wi = self._evaluate(data_row['DLY-SNWD-PCTALL-GE010WI'])
        self.dly_snwd_pctall_ge003wi = self._evaluate(data_row['DLY-SNWD-PCTALL-GE003WI'])
        self.dly_snwd_pctall_ge005wi = self._evaluate(data_row['DLY-SNWD-PCTALL-GE005WI'])
        self.dly_snow_pctall_ge001ti = self._evaluate(data_row['DLY-SNOW-PCTALL-GE001TI'])
        self.dly_snow_pctall_ge010ti = self._evaluate(data_row['DLY-SNOW-PCTALL-GE010TI'])
        self.dly_snow_pctall_ge100ti = self._evaluate(data_row['DLY-SNOW-PCTALL-GE100TI'])
        self.dly_snow_pctall_ge030ti = self._evaluate(data_row['DLY-SNOW-PCTALL-GE030TI'])
        self.dly_snow_pctall_ge050ti = self._evaluate(data_row['DLY-SNOW-PCTALL-GE050TI'])
        self.dly_tavg_normal = self._evaluate(data_row['DLY-TAVG-NORMAL'])
        self.dly_dutr_normal = self._evaluate(data_row['DLY-DUTR-NORMAL'])
        self.dly_tmax_normal = self._evaluate(data_row['DLY-TMAX-NORMAL'])
        self.dly_tmin_normal = self._evaluate(data_row['DLY-TMIN-NORMAL'])
        self.dly_tavg_stddev = self._evaluate(data_row['DLY-TAVG-STDDEV'])
        self.dly_dutr_stddev = self._evaluate(data_row['DLY-DUTR-STDDEV'])
        self.dly_tmax_stddev = self._evaluate(data_row['DLY-TMAX-STDDEV'])
        self.dly_tmin_stddev = self._evaluate(data_row['DLY-TMIN-STDDEV'])

    def __repr__(self):
        return str(self.to_dict())

    def to_dict(self):
        return self.__dict__

    def _evaluate(self, input_data):

        if input_data in ['-9999', '-66.6', '-666']:
            return None
        else:
            try:
                return float(input_data)
            except ValueError:
                return None


class VanguardTransaction:
    def __init__(self, data_row):
        pass
