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


notMonitoredD = {}
errorConditionsD = {}
fullServiceListD = {}
for server in parsedXML:
    address = server.find('./server//httpd//')
    for service in server.findall('service'):
        serviceType = service.attrib
        name = service.find('name')
        monitorStatus = service.find('monitor')
        status = service.find('status')
        errorStatus = service.find('status_message')
        if not errorStatus:
            errorStatus = "None"
        else:
            errorStatus = errorStatus.text
        if monitorStatus.text == "0": #If not monitored
            #notMonitoredD[address.text] = [name.text, status.text, errorStatus.text]
            notMonitoredD[address.text] = [address.text, name.text, status.text, errorStatus]

        if errorStatus != "None" or status.text == "4608": #if it has an error message, or error code ##todo## (find error codes)
            errorConditionsD[address.text] = [address.text, name.text, status.text, errorStatus]
        fullServiceListD[address.text] = [address.text, serviceType[class], name.text, status.text, errorStatus]


#for items,keys in errorConditionsD.items():
#    print(items)
#    print(keys[1])


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

@app.route("/services")
def services():
    return render_template('services_template.html', notMonitoredD = notMonitoredD, errorConditionsD = errorConditionsD, title="Full Service List")

@app.route("/home")
def home():
    return render_template('base_template.html', failedServers = failedServers, notMonitored = notMonitoredD, errorConditionsD = errorConditionsD, title="Home - Main Server Overview")

@app.route("/about")
def about():
    return render_template('base_template.html', my_string="Bar",
        my_list=[12,13,14,15,16,17], title="About", current_time=datetime.datetime.now())

@app.route("/servers")
def servers():
    return render_template('server_template.html', title="Server List", respondingServers=respondingServers, failedServers=failedServers)


if __name__ == '__main__':
    app.run(debug=True)