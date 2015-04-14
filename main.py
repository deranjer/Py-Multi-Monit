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
for server in serverList: #generating server API URL's
    list.append(APIURL, "http://%s:2812/_status?format=xml" %server)

#URL = "http://192.168.1.100:2812/_status?format=xml"


def infoRefresh():
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

    id=0
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
            #if not errorStatus:
            if errorStatus == None:
                errorStatus = "None"
            else:
                errorStatus = errorStatus.text
            if monitorStatus.text == "0": #If not monitored
                #notMonitoredD[address.text] = [name.text, status.text, errorStatus.text]
                notMonitoredD[id] = [address.text, name.text, status.text, errorStatus]

            if errorStatus != "None" or status.text != "0": #if it has an error message, or error code ##todo## (find error codes)
                errorConditionsD[id] = [address.text, name.text, status.text, errorStatus]
            #print(serviceType['type'])
            #serviceTypeClass = serviceType['type']
            localLink = '<a href="http://%s:2812/%s">%s</a>' % (address.text, name.text, name.text)
            fullServiceListD[id] = [address.text, serviceType['type'], name.text, status.text, localLink]
            id += 1 #internal ID for lists
            #print(fullServiceListD[address.text])
    return {'notMonitoredD' : notMonitoredD, 'errorConditionsD': errorConditionsD, 'fullServiceListD' : fullServiceListD, 'failedServers' : failedServers, 'respondingServers' : respondingServers}


#for items,keys in errorConditionsD.items():
#    print(items)
#    print(keys[1])


#objend = obj.monit.server.httpd.address.cdata

#@app.before_first_request
#rootElem = parsedXML[0].getroot()
infoRefresh()


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
    infoRefreshResults =  infoRefresh()
    return render_template('services_template.html', notMonitoredD=infoRefreshResults['notMonitoredD'], errorConditionsD=infoRefreshResults['errorConditionsD'], fullServiceListD=infoRefreshResults['fullServiceListD'], title="Full Service List")

@app.route("/home")
def home():
    infoRefreshResults = infoRefresh()
    return render_template('base_template.html', failedServers = infoRefreshResults['failedServers'], notMonitored = infoRefreshResults['notMonitoredD'], errorConditionsD = infoRefreshResults['errorConditionsD'], title="Home - Main Server Overview")

@app.route("/about")
def about():
    return render_template('base_template.html', my_string="Bar",
        my_list=[12,13,14,15,16,17], title="About", current_time=datetime.datetime.now())

@app.route("/servers")
def servers():
    infoRefreshResults = infoRefresh()
    return render_template('server_template.html', title="Server List", respondingServers=infoRefreshResults['respondingServers'], failedServers=infoRefreshResults['failedServers'])


if __name__ == '__main__':
    app.run(debug=True)