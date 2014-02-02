#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import json
import select
from urlparse import urlparse
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = int(code)
        self.body = body

class HTTPClient(object):

    def test(self):
	
	parseUrl = urlparse('http://www.google.ca')
	if parseUrl.port == None:
		s = self.connect(parseUrl.hostname,80)
	else:
		s= self.connect(parseUrl.hostname,parseUrl.port)
	s.send('GET / HTTP/1.1\r\nAccept: */*\r\n\r\n')
	data = ""
	s.setblocking(0)
	ready = select.select([s], [],[],1)
	while ready[0]:
		data += s.recv(1024)
		ready = select.select([s], [],[],1)
	s.close()

    def connect(self, host, port):
        # use sockets!
	if port == None:
		port = 80
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect((host,port))
	return s

    def get_code(self, data):
        return data.split('\n', 1)[0].split(' ')[1]

    def get_headers(self,data):
	str = data.replace(data.split('\n')[0]+'\n','')
        return str.split('\r\n\r\n')[0]

    def get_body(self, data):
	str = data.replace(data.split('\n')[0]+'\n','')
        return str.split('\r\n\r\n')[1]

    # read everything from the socket
    def recvall(self, sock):
	buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)
    def test2(self):
	req = self.GET("http://www.google.ca")

    def GET(self, url, args=None):
	parseUrl = urlparse(url)
	s = self.connect(parseUrl.hostname,parseUrl.port)
	send = self.buildRequestString("GET",url,args)
	s.send(send)
	message = self.recvall(s)
	code = self.get_code(message)
	body = self.get_body(message)
        return HTTPRequest(code, body)

    def buildRequestString(self,type,url, args):
	ce = "identity"
	ct = "application/x-www-form-urlencoded"
	host = urlparse(url).hostname
	path = urlparse(url).path
	accept = '*/*'
	if type == "POST":
		s  = 'POST ' + path + ' HTTP/1.1\r\n'
	else:
		s = 'GET ' + path + ' HTTP/1.1\r\n'
	s += 'User-Agent: curl/7.21.4 (universal-apple-darwin11.0) libcurl/7.21.4 OpenSSL/0.9.8x zlib/1.2.5\r\n'
	s += 'Host: ' + host + '\r\n'
	s += 'Accept: ' + accept + '\r\n'
	#s += 'Content-Encoding: ' + ce + '\r\n'
	#s += 'Content-Type: ' + ct + '\r\n'
	if args!=None:
		body = self.buildString(args)
		cl = str(len(body)) + '\r\n'
		s += 'Content-Length: ' + cl + '\r\n'
		s += body + '\r\n'
	s += '\r\n'
	print s
	return s
		
    def buildString(self,args):
	s = ""
	for key in args:
		s += key + '=' + args[key]
		s += '&'
	return s 
    def POST(self, url, args=None):
	parseUrl = urlparse(url)
	s = self.connect(parseUrl.hostname,parseUrl.port)
	send = self.buildRequestString("POST",url,args) 

	s.send(send)
	message = self.recvall(s)
	code = self.get_code(message)
        body = self.get_body(message)
	return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    

