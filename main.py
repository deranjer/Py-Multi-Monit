__author__ = 'deranjer'

#import bs4
import datetime
import urllib
#import pprint #used for printing XML trees
import xml.etree.ElementTree as ET #cElemetTree is depreciated apparently
from Settings import serverList
from flask import Flask, render_template, redirect
app = Flask(__name__, template_folder='Templates')


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


def parseServers():
    parsedXML = []
    failedServers = []
    for URL in APIURL:
        try:
            print("URL", URL)
            file = urllib.request.urlopen(URL) #opening the XML URL
            list.append(parsedXML, ET.parse(file)) #Parsing the XML file using Celementtree
        except:
            list.append(failedServers, URL) #if the server doesn't respond, add it to the failed server list
    respondingServersD = {}
    id = 0 #internal ID for keyed list
    for server in parsedXML:
        address = server.find('./server//httpd//')
        localServerLink = '<a href="http://%s:2812">%s</a>' % (address.text, address.text) #link to internal server
        serverRoot = server.find('./server')
        monitVersion = serverRoot.find('version').text
        count = 0 #defining the counter for the number of services per server.
        errorCount = 0 # defining the number of services in error for each server.
        for service in server.findall('service'): #Counting the number of services per server
            count +=1
            status = service.find('status')
            errorStatus = service.find('status_message')#todo status_message may not exist?
            if errorStatus != None or status.text != "0":
                errorCount += 1
        respondingServersD[id] = [address.text, localServerLink, monitVersion, count, errorCount]
        id += 1
    return {'failedServers' : failedServers, 'respondingServersD' : respondingServersD, 'parsedXML' : parsedXML}

def errorStatusF(service): #function to find out if there is an error status on a job
    status = service.find('status')
    errorStatus = service.find('status_message')
    if errorStatus == None:
        errorStatus = "None"
    else:
        errorStatus = errorStatus.text
    return (errorStatus, status)


def infoRefresh(): #called each page load, just reparses the XML to make sure nothing changed
    parseServersResults = parseServers() #parsing all of the XML again...
    id=0 #creating internal ID to sort lists by, etc.
    notMonitoredD = {} #list of services that are "not monitored" by monit
    errorConditionsD = {} #list of error condition services
    fullServiceListD = {}
    for server in parseServersResults['parsedXML']:
        address = server.find('./server//httpd//')
        for service in server.findall('service'):
            serviceType = service.attrib
            name = service.find('name')
            monitorStatus = service.find('monitor')

            errorStatus, status = errorStatusF(service) #finding an error status

            if errorStatus != "None" or status.text != "0": #if it has an error message, or error code ##todo## (find error codes)
                errorConditionsD[id] = [address.text, name.text, status.text, errorStatus]

            if monitorStatus.text == "0": #If not monitored
                notMonitoredD[id] = [address.text, name.text, status.text, errorStatus]
            localLink = '<a href="http://%s:2812/%s">%s</a>' % (address.text, name.text, name.text) #link to internal server service
            fullServiceListD[id] = [address.text, serviceType['type'], name.text, status.text, localLink]
            id += 1 #internal ID for lists
            #print(fullServiceListD[address.text])
    return {'notMonitoredD' : notMonitoredD, 'errorConditionsD': errorConditionsD, 'fullServiceListD' : fullServiceListD }


def countServices(): #TODO Might not need this
    parseServersResults = parseServers()
    print("counting")
    count = 0
    for server in parseServersResults['parsedXML']:
        address = server.find('./server//httpd//')
        for service in server.findall('service'):
            count +=1



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
    parseServersResults = parseServers()
    return render_template('base_template.html', failedServers = parseServersResults['failedServers'], notMonitored = infoRefreshResults['notMonitoredD'], errorConditionsD = infoRefreshResults['errorConditionsD'], title="Home - Main Server Overview")

@app.route("/about")
def about():
    return render_template('about.html', title="About Py-Multi-Monit")

@app.route("/servers")
def servers():
    parseServersResults = parseServers()
    respondingServersD=parseServersResults['respondingServersD']
    print("HERE IS YOUR SHIT")
    print(*respondingServersD, sep='\n')
    #return render_template('server_template.html', title="Server List", respondingServers=parseServersResults['respondingServers'], failedServers=parseServersResults['failedServers'])
    return render_template('server_template.html', title="Server List", respondingServersD=parseServersResults['respondingServersD'], failedServers=parseServersResults['failedServers'])

@app.route('/servers/<serverIP>')
def serverByIP(serverIP):
    """todo get all services for that server"""
    return render_template('server_by_ip_template.html', title=serverIP)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
