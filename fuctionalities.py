from datetime import date, timedelta
from pandas import read_csv
from statsmodels.tsa.arima.model import ARIMA
import numpy

def conv_str_date(date1):
    y,m,d = date1.split("-")
    y,m,d = int(y),int(m),int(d)
    x = date(2021, 3, 30) 
    return x

def find_between_dates(start1,end1):
    delta = end1 - start1       # as timedelta
    result = []
    for i in range(delta.days + 1):
        day = start1 + timedelta(days=i)
        day = str(day)
        result.append(day)
    return  result


def predict_next(series, categ):
    
    days_in_year = 365
    differenced = series[[categ]]
    model = ARIMA(differenced, order=(1,1,1))
    model_fit = model.fit()
    forecast = model_fit.forecast()

    return forecast

