__author__ = 'deranjer'

import bs4
import datetime
import urllib
import pprint
import xml.etree.ElementTree as ET
from Settings import serverList
from flask import Flask, render_template, redirect
app = Flask(__name__)


#Generate list of servers from config file
#for now fake file
#serverList = []
#read from file here...

#for now fake
#list.append(serverList, '192.168.1.100')
#list.append(serverList, '192.168.1.150')
APIURL = []
for server in serverList:
    list.append(APIURL, "http://%s:2812/_status?format=xml" %server)

#URL = "http://192.168.1.100:2812/_status?format=xml"



parsedXML = []
failedServers = []
for URL in APIURL:
    try:
        print("URL", URL)
        file = urllib.request.urlopen(URL) #opening the XML URL
        list.append(parsedXML, ET.parse(file)) #Parsing to dict the XML file created
    except:
        list.append(failedServers, URL)

respondingServers = []
for server in parsedXML:
    address = server.find('./server//httpd//')
    list.append(respondingServers, address.text)


notMonitored = []
errorConditionsL = {}
errorConditionsD = {}
for server in parsedXML:
    address = server.find('./server//httpd//')
    for service in server.findall('service'):
        name = service.find('name')
        monitorStatus = service.find('monitor')
        monitorStatus = monitorStatus.text
        if monitorStatus == "0":
            list.append(notMonitored, name.text)
            print("NOT MONITORED", name.text)
        errorStatus = service.find('status_message')
        #errorStatusText = errorStatus.text
        if errorStatus != None:
            #errorConditionsD[name.text]=[errorStatus.text]
            #errorConditionsL


print(errorConditions)
for keys,values in errorConditions.items():
    print(keys, values)

#objend = obj.monit.server.httpd.address.cdata

#@app.before_first_request
#rootElem = parsedXML[0].getroot()



@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

app.jinja_env.filters['datetimefilter'] = datetimefilter

@app.route("/")
def template_test():
    return redirect("/home", code=302)

@app.route("/backend")
def backend():
    return objjson

@app.route("/home")
def home():
    return render_template('base_template.html', failedServers = failedServers, notMonitored = notMonitored, errorConditions = errorConditions, title="Home - Main Server Overview")

@app.route("/about")
def about():
    return render_template('base_template.html', my_string="Bar",
        my_list=[12,13,14,15,16,17], title="About", current_time=datetime.datetime.now())

@app.route("/servers")
def servers():
    return render_template('server_template.html', title="Server List", respondingServers=respondingServers)


if __name__ == '__main__':
    app.run(debug=True)