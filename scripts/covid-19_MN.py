'''
Plot COVID-19 data

Created on 1 Apr 2020
@author: mnobakht
'''
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')
import datetime
import numpy as np

def main():
    #data
    confirmed = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
    death = pd.read_csv(u'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')
    countryList = confirmed['Country/Region'].to_list()
    
    #Read country data
    #------------------------------------------------------------------------------ 
    countries = ['Italy', 'United Kingdom']
    #------------------------------------------------------------------------------
    
    fig, ax = plt.subplots(figsize=(7,4))
    ax2 = ax.twinx()

    for country in countries: 
        if country not in countryList:
            raise ValueError('Select from the folowwing list:\n{}'.format(countries))
        countryConf =  confirmed[confirmed['Country/Region'] == country]
        countryDeath =  death[death['Country/Region'] == country]
        
        #Select country data, not the province/state/territory
        if country not in ['China', 'Canada']:
            countryConf = countryConf[pd.isna(countryConf['Province/State'])]
            countryDeath = countryDeath[pd.isna(countryDeath['Province/State'])]
        
        #Time series
        if country in ['China', 'Canada']:
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
        confRollAvg = confDaily[confDaily[country].notnull()].rolling(10).mean()
        deathRollAvg = deathDaily[deathDaily[country].notnull()].rolling(10).mean()
         
        #Plot
        confDaily.plot(y = country, marker = 'o', linewidth = 0, ax=ax, label = '_nolegend_', markersize = 4, alpha = 0.5)
        deathDaily.plot(y = country, marker = 'P', linewidth = 0, ax=ax2, label = '_nolegend_', markersize = 4, alpha = 0.5)
        confRollAvg.plot(y = country, ax=ax, label= '{} (Confirmed)'.format(country))
        deathRollAvg.plot(y = country, linestyle= '--',ax=ax2, label = '{} (Death)'.format(country))
        
    ax.set_xlim([confDaily.index[0]-datetime.timedelta(5), confDaily.index[-1]+datetime.timedelta(5)])
    ax.set_title('Daily Confirmed Cases of COVID-19\n{0} to {1}'.format(datetime.datetime.strftime(confDaily.index[0],'%Y-%m-%d'),
                                                               datetime.datetime.strftime(confDaily.index[-1],'%Y-%m-%d')))
    ax.set_xlabel('Date')
    ax.set_ylabel('Confirmed Cases')
    ax2.set_ylabel('Death')
    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.get_legend().remove()
    ax2.get_legend().remove()
    ax2.legend(lines + lines2, labels + labels2, loc=0)
    plt.show()
    
if __name__ == '__main__':
    main()
    print('Done')
    