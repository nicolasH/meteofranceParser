## meteofrance parser

This project is used to parse the meteofrance.com page about a city. It will read the information that are contained in the forecast table and write it in a flat html table. Since they are now (July 2010) published on the same page, the forecast now also includes the tendances. 

There are two part: 
- The weather.py script is useful for simplifying the html of the original meteofrance page. - The main.py and me.py are used when the script is run on the google app engine.

## When run locally : 

The main script is "weather.py". It parse the pages given in the names.txt and writes the output every hour.
A sample of the expectd input is the "names.txt" file, which the "weather.py" script reads by default.
The input file is determined in the "weather.py" script, as well as the name of the generated html index file and the directory in which the html output will be generated.

The generated output html import some very basic styling defined in the "weather.css".

The input file has to contain a user given name for the city, the meteofrance domain, the url on the domain, as well as the name of the file that will contain the simplified forecast. Here is an example :

Prevessin,http://france.meteofrance.com/,france/meteo?PREVISIONS_PORTLET.path=previsionsville/013130,meteo_prevessin.html,

- The city will be called "Prevessin" in the output file, which will be called "meteo_prevessin.html". 
- The data will be from the domain "http://france.meteofrance.com/" and the actual forecast will be parsed from: "http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/013130".


## When run on app engine : 

A basic homepage containing links described in the names.txt is generated

Individual cites are available in the /there/mo/12345 or /there/fr/123456 format.
/there/mo/ is for 'world' cities and /there/fr/ for 'french' mainland cities. The code is last digits in the url of the cities when you look at the forecast for an individual city.

You can save your favorite cities by going to the /me url.



This project is released under the GPLv2 License that you can find at http://www.gnu.org/licenses/gpl-2.0.txt. Learn more about the GPL here http://www.gnu.org/licenses/gpl-2.0.html

Copyright (c) Nicolas Hoibian 2009-2010.
