import pandas as pd
import numpy as np
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import datetime
import warnings
from plotly.subplots import make_subplots
import plotly.graph_objs as go
warnings.filterwarnings('ignore')


#data
confirmed = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
death = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
countryList = confirmed['Country/Region'].unique()
countryList.sort()

def getCountryStats(country,window):
    '''
    To extract statistics for the given country.
    Returns pd.DataFrame
    '''
    retDf = pd.DataFrame()
    dfDict = {'Confirmed':confirmed, 'Death': death}
    firstIndexList = []
    
    for dfName in dfDict:
        df = dfDict[dfName]
        countryDf =  df[df['Country/Region'] == country]
        
        #Select country data, not the province/state/territory
        if country not in ['China', 'Canada', 'Australia']:
            countryDf = countryDf[pd.isnull(countryDf['Province/State'])]
            
        #Time series
        if country in ['China', 'Canada', 'Australia']:
            Ts = pd.DataFrame(countryDf.sum(0)[4:])
        else:
            Ts = countryDf.transpose()[4:]

        Ts.columns = [country]
        
        #Get index of the date to reach 20 confirmed cases
        firstIndexList.append(Ts.astype('float64')[Ts>=20].idxmin())

        #convert cumulative data to daily stats
        daily = Ts.diff()
        daily.index = pd.to_datetime(daily.index)

        #Rolling average
        rollAvg = daily[daily[country].notnull()].rolling(window).mean()

        #Add to return dataframe
        retDf[dfName] = daily[country]
        retDf[dfName+'_'+'rollAvg'] = rollAvg
        retDf.index = daily.index
    
    try:
        startDate = pd.DataFrame(firstIndexList).min().get_values()[0]
        retDf = retDf[retDf.index>=startDate]
    except:
        pass
    
    return retDf

@interact(Country1=countryList,Country2=countryList,Country3=countryList, RollingAvg = (2,20))
def plot(Country1='United Kingdom', Country2='Italy',Country3='Spain', RollingAvg = 10):
    countries = [Country1, Country2, Country3]
    
    fig = make_subplots(rows=2, cols=1,
                        subplot_titles=('Daily Confirmed Death', 'Daily Confirmed Cases'),
                        vertical_spacing = 0.1,
                        shared_xaxes=True,
                        x_title='Date')
    
    colours = ['#6077d1', '#2d8040', '#ba2736']
    cIndex = 0
    
    for country in countries:
        df = getCountryStats(country,RollingAvg)
                
        #Plot
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Death_rollAvg'],
                name=country,
                showlegend=False,
                line=dict(width=3,color=colours[cIndex])),
            row=1, col=1)
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Death'],
                showlegend=False,
                marker=dict(color=colours[cIndex]),opacity=0.4),
            row=1, col=1)
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Confirmed_rollAvg'],
                name=country,
                line=dict(width=3,color=colours[cIndex])),
            row=2, col=1)
        
        fig.add_trace(
            go.Bar(
                x=df.index,
                y=df['Confirmed'],
                name=country,
                showlegend=False,
                marker=dict(color=colours[cIndex]),opacity=0.4),
            row=2, col=1)
        
        cIndex+=1

    fig.update_layout(height=800, width=1000,
                      title_text="<b>COVID-19 Daily Stats</b><br />(Last Update {})".format(datetime.datetime.strftime(df.index[-1],
                                                                                                                       '%Y-%m-%d')),
                      legend_title='<b>{} Day Rolling Avg</b>'.format(RollingAvg),
                     legend=dict(x=0.01, y=0.99),
                     template='plotly_dark')

    fig.show()
