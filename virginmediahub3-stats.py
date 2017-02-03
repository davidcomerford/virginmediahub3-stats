import requests
import collections
from requests import Request, Session
import xml.etree.ElementTree as ET

"""
Variables
"""
# Source of data
url = "http://192.168.0.1/common_page/login.html"
posturl = "http://192.168.0.1/xml/getter.xml"
datatopost = ""

# Destination for data
# You should change your influxDB hostname, retention policy and database name
influxurl = "http://hector:8086/write?db=virginmediahub"


# Create a session
# We need this to get the session ID which is sent as 'token' in the POST
s = requests.Session()
r = s.get(url)
token = s.cookies['sessionToken']

"""
Downstream data gathering
"""
# 'fun: 10' is to fetch the downstream data
payload = collections.OrderedDict([('token', token), ('fun', '10')])

req = Request('POST', posturl, data=payload, headers={})
prepped = s.prepare_request(req)
prepped.headers['Content-Type']
r = s.send(prepped, stream=False, timeout=None, verify=True, cert=None, proxies=None)

# Refresh token variable with new session ID
token = s.cookies['sessionToken']

# Process the returned XML data
root = ET.fromstring(r.content)

for child in root.iter('downstream'):
    channelid = child.find('chid').text
    power = child.find('pow').text
    snr = child.find('snr').text

    datatopost += """
downstream,channel=%s power=%s,snr=%s""" % (channelid, power, snr)

"""
Upstream data gathering
"""
# 'fun: 11' is to fetch the upstream data
upstreampayload = collections.OrderedDict([('token', token), ('fun', '11')])

upstreamreq = Request('POST', posturl, data=upstreampayload, headers={})
prepped = s.prepare_request(upstreamreq)
prepped.headers['Content-Type']
r = s.send(prepped, stream=False, timeout=None, verify=True, cert=None, proxies=None)

# Refresh token variable with new session ID
token = s.cookies['sessionToken']

# Lets process the returned XML data
root = ET.fromstring(r.content)

for child in root.iter('upstream'):
    channelid = child.find('usid').text
    power = child.find('power').text

    datatopost += """
upstream,channel=%s power=%s""" % (channelid, power)


"""
Operational state
Graphana isn't great with strings so I'm storing the 'provisioned state' to an integer.
'Online' is 0 and will be the colour green in a Graphana Text panel
Contains 'Online' in some form is 1 and will be yellow
Contains 'Offline' in some form will be red
"""
# 'fun: 144' is to fetch the operational data
statepayload = collections.OrderedDict([('token', token), ('fun', '144')])
statereq = Request('POST', posturl, data=statepayload, headers={})
prepped = s.prepare_request(statereq)
prepped.headers['Content-Type']
r = s.send(prepped, stream=False, timeout=None, verify=True, cert=None, proxies=None)

# XML processing
root = ET.fromstring(r.content)
textstate = root.find('provisioning_st').text

if textstate == "Online":
    intstate = 0
elif "Online" in textstate:
    intstate = 1
elif "Offline" in textstate:
    intstate = 2
else: intstate = 3

datatopost += """
status state=%i""" % (intstate)


"""
Send to InfluxDB
"""
req = Request('POST', influxurl, data=datatopost)
prepped = req.prepare()
r = s.send(prepped, stream=False, timeout=None, verify=True, cert=None, proxies=None)
