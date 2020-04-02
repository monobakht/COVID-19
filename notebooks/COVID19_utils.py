import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
from IPython.display import display
import datetime
import warnings
warnings.filterwarnings('ignore')

#data
confirmed = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
death = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
countryList = confirmed['Country/Region'].to_list()

@interact(Country1=countryList,Country2=countryList,Country3=countryList, Average = (2,20))
def plot(Country1='United Kingdom', Country2='Italy',Country3='Spain', Average = 10):
    countries = [Country1, Country2, Country3]
    plt.style.use('ggplot')
    fig, ax = plt.subplots(figsize=(15,8))
    ax2 = ax.twinx()
    colours = ['#6077d1', '#2d8040', '#ba2736']
    cIndex = 0

    for country in countries:
        countryConf =  confirmed[confirmed['Country/Region'] == country]
        countryDeath =  death[death['Country/Region'] == country]

        #Select country data, not the province/state/territory
        if country not in ['China', 'Canada', 'Australia']:
            countryConf = countryConf[pd.isna(countryConf['Province/State'])]
            countryDeath = countryDeath[pd.isna(countryDeath['Province/State'])]

        #Time series
        if country in ['China', 'Canada', 'Australia']:
            confTs = pd.DataFrame(countryConf.sum(0)[4:])
            deathTs = pd.DataFrame(countryDeath.sum(0)[4:])
        else:
            confTs = countryConf.transpose()[4:]
            deathTs = countryDeath.transpose()[4:]

        confTs.columns = [country]
        confDaily = confTs.diff()
        confDaily.index = pd.to_datetime(confDaily.index)

        deathTs.columns = [country]
        deathDaily = deathTs.diff()
        deathDaily.index = pd.to_datetime(deathDaily.index)

        #Rolling average
        confRollAvg = confDaily[confDaily[country].notnull()].rolling(Average).mean()
        deathRollAvg = deathDaily[deathDaily[country].notnull()].rolling(Average).mean()

        #Plot
        colour = colours[cIndex]
        confDaily.plot(y = country, marker = 'o', linewidth = 0, ax=ax, label = '_nolegend_',
                       markersize = 6, markeredgewidth=0, alpha = 0.5,c=colour)
        deathDaily.plot(y = country, marker = 'P', linewidth = 0, ax=ax2, label = '_nolegend_',
                        markersize = 6, markeredgewidth=0, alpha = 0.5,c=colour)
        confRollAvg.plot(y = country, ax=ax, label= '{} (Confirmed)'.format(country),c=colour)
        deathRollAvg.plot(y = country, linestyle= '--',ax=ax2, label = '{} (Death)'.format(country),c=colour)
        
        cIndex+=1

    ax.set_xlim([confDaily.index[0]-datetime.timedelta(5), confDaily.index[-1]+datetime.timedelta(5)])
    ax.set_title('Daily Confirmed Cases of COVID-19\n{0} to {1}'.format(datetime.datetime.strftime(confDaily.index[0],'%Y-%m-%d'),
                                                               datetime.datetime.strftime(confDaily.index[-1],'%Y-%m-%d')))
    ax.set_xlabel('Date')
    ax.set_ylabel('Confirmed Cases (o)')
    ax2.set_ylabel('Death (+)')
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.get_legend().remove()
    ax2.get_legend().remove()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    plt.show()
    