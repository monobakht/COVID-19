import pandas as pd
import numpy as np
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import datetime
import warnings
from plotly.subplots import make_subplots, _get_grid_subplot
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
def plot(Country1='United Kingdom', Country2='Italy',Country3='Spain', RollingAvg = 5):
    countries = [Country1, Country2, Country3]
    
    fig = make_subplots(subplot_titles=('Daily Number of Confirmed Cases & Deaths',),
                        vertical_spacing = 0.1,
                        shared_xaxes=True,
                        x_title='Date',
                        specs=[[{"secondary_y": True}]])
    
    colours = ['#6077d1', '#2d8040', '#ba2736']
    cIndex = 0
    maxDeath = 0
    maxConf = 0
    
    for country in countries:
        df = getCountryStats(country,RollingAvg)
        
        #Get data range
        if df['Confirmed'].max() > maxConf:
            maxConf = df['Confirmed'].max()
        if df['Death'].max() > maxDeath:
            maxDeath = df['Death'].max()
            
        #Plot
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Confirmed'],
                name=country+' (Cases)',
                showlegend=False,
                mode='markers',
                marker=dict(color=colours[cIndex]),opacity=0.4))
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Death'],
                name = country+' (Death)',
                showlegend=False,
                mode='markers',
                marker=dict(color=colours[cIndex]),opacity=0.4, marker_symbol='cross'),
        secondary_y=True)
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Confirmed_rollAvg'],
                name=country+' (Cases)',
                legendgroup=country,
                line=dict(width=3,color=colours[cIndex])))
        
        fig.add_trace(
            go.Scatter(
                x=df.index,
                y=df['Death_rollAvg'],
                name=country+' (Death)',
                legendgroup=country,
                line=dict(width=3,color=colours[cIndex],dash='dot')),
            secondary_y=True)
        
        cIndex+=1

    #sync axis range to overlay grids
    rangeMax = max(maxDeath*10, maxConf)
    yMax = ((rangeMax//1000)+3)*1000
    yRange = list(range(0,yMax,1000))
    y2Range = list(range(0,int(yMax/10),100))
    
    if len(yRange)<5:
        yMax = ((rangeMax//100)+3)*100
        yRange = list(range(0,yMax,100))
        y2Range = list(range(0,int(yMax/10),10))
        
    while len(yRange)>12 :
        yRange = yRange[::2]
        y2Range = y2Range[::2]
        
    #Set plot layout
    fig.update_layout(height=600, width=900,
                    title_text="<b>COVID-19 Daily Stats</b><br />(Last Update {})".format(datetime.datetime.strftime(df.index[-1],
                                                                                                                   '%Y-%m-%d')),
                    legend_title='<b>{} Day Rolling Avg</b><br />'.format(RollingAvg),
                    legend=dict(x=0.05, y=0.90, bordercolor="White", borderwidth=1),
                    template='plotly_dark',
                    xaxis= dict(showgrid = False),
                    yaxis = dict(range=(0,yRange[-1]), tickvals = yRange[:-1]),
                    yaxis2 = dict(range=(0,y2Range[-1]), tickvals = y2Range[:-1]),
                    margin=dict(b=60, t=125, r=25)
                    )
    fig.update_yaxes(title_text="<b>Confirmed Cases (o)</b>", secondary_y=False)
    fig.update_yaxes(title_text="<b>Confirmed Death (+)</b>", secondary_y=True)

    fig.show()
