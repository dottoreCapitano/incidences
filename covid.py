import datetime
from matplotlib import (pyplot as plt, dates)
import os
import requests


def makeIndex(response):
    countries = {}

    for i in range(len(response['records'])):
        if response['records'][i]['popData2019'] != '' and response['records'][i]['countryterritoryCode'] != 'N/A':
            countries.update({response['records'][i]['countryterritoryCode']: response['records'][i]['countriesAndTerritories']})
            
    for country in countries:
        print(country, countries[country])

    return countries


def filterForCountry(response, country):
    d = {}

    for i in range(len(response['records'])):
        if response['records'][i]['countryterritoryCode'] == country:
            d[datetime.datetime(int(response['records'][i]['year']), int(response['records'][i]['month']), int(response['records'][i]['day']))] = int(response['records'][i]['cases'])
            population = int(response['records'][i]['popData2019'])

    return d, population


def computeIncidences(d, period, population):
    dateKeys = list(d.keys())
    dateKeys.sort()

    dateValues = []
    incidences = []
    x = [0] * period

    for i in range(len(dateKeys)):
        if i > period - 2:
            for j in range(period):
                x[j] = d[dateKeys[i - j]]
            incidence = sum(x)/population*100000

            print(str(dateKeys[i])[:10], end=' ')
            for j in range(period):
                print(x[period - j - 1], end=' ')
            print(incidence, '[', population/1000000, ']')

            dateValues.append(dates.date2num(dateKeys[i]))
            incidences.append(incidence)

    return dateValues, incidences


def plotIncidences(dateValues, incidences, period, country, countries):
    fill = [True] * len(incidences)
    for i in range(len(incidences)):
        fill[i] = incidences[i] >= 50
    plt.plot_date(dateValues, incidences, '-')
    plt.fill_between(x = dateValues, y1 = incidences, where = fill, color = 'red', alpha = 1)
    plt.yscale('linear')
    plt.title(str(period) + ' day incidences ' + country + ' (' + countries[country] + ')')
    plt.grid()
    plt.xticks(plt.xticks()[0], rotation=90)
    plt.savefig('png/' + country + '.png')
    plt.show()


PERIOD = 7
COUNTRIES = ['CHE', 'FRA', 'GBR', 'CZE', 'HUN', 'PRT', 'ESP', 'BEL', 'BGR', 'GRC', 'MLT', 'AUT', 'ITA', 'DEU', 'SWE', 'USA', 'NLD', 'HRV', 'MEX', 'SVN']

print('Fetch data from European Centre for Disease Prevention and Control ...')

response = requests.get('https://opendata.ecdc.europa.eu/covid19/casedistribution/json').json()

print('... Download finished.')

complete = {}

countryIndex = makeIndex(response)

os.makedirs('png', exist_ok=True)

for country in COUNTRIES:
    d, population = filterForCountry(response, country)
    dateValues, incidences = computeIncidences(d, PERIOD, population)
    complete[country] = [dateValues, incidences]
    plotIncidences(dateValues, incidences, PERIOD, country, countryIndex)

for country in COUNTRIES:
    plt.plot_date(complete[country][0], complete[country][1], '-', label=country)
plt.title(str(PERIOD) + ' day incidences')
plt.grid()
plt.xticks(plt.xticks()[0], rotation=90)
plt.legend(loc='upper left')
plt.savefig('png/all.png')
plt.show()
