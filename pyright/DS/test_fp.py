import pandas as pd

def f_18684076():
    """create a list of date string in 'yyyymmdd' format with Python Pandas from '20130226' to '20130302'
    """
    start_date = '20130226'
    end_date = '20130302'
    
    date_range = pd.date_range(start=start_date, end=end_date, format='%Y%m%d')
    date_strings = date_range.strftime('%Y%m%d').tolist()
    
    return date_strings

f_18684076()