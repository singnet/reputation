# MIT License
# 
# Copyright (c) 2018-2019 Stichting SingularityNET
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# HOWTO: Using this API with Aigents server
# TODO: Explain steps to get Aignts server running as quickly as possible

# TODO: Complete the test suite functions


import sys
import requests
from urllib.parse import quote

# Expected Aigents server version 
version = "1.5.5"

# Expected Aigents copyright information
copyright = " Copyright © 2019 Anton Kolonin, Aigents."

# URL to Aigents server
base_url = "http://localtest.com:1180/?"

# Whether to log debugging output or keep silent
verbose = True

# Indicate if test suite is failed
failed  = 0

# Default HTTP session to Aigents server
session = None

# Last reponse text got from Aigents server on say() call 
last_in = None


def gettext(text = None):
	"""
	Submit request to Aigents and get response text.
	Args:
		text - submitted request text
	Returns:
		text of the response
	"""
	global base_url
	global session
	if session is None:
		session = requests.Session()
	request = base_url + quote(text)
	r = session.post(request)
	return r.text


def getdata(text = None):
	"""
	Submit request to Aigents and get line of status response text
	with following multi-line tab-delimited response text.
	Args:
		text - submitted request text
	Returns:
		status - text of status returned
		list - list of lists accordingly to parsed multi-line tab-separated response text
	"""
	res = gettext(text)
	if res is None:
		return
	list = []
	status = None
	for line in res.splitlines():
		if status is None:
			status = line
		else:
			list.append(line.split('\t'))
	return status, list


def say(text = None):
	"""
	Submit request to Aigents and get the response retained for further call to get().
	Print the request if verbose is set to True.
	Args:
		text - submitted request text
	Returns:
		nothing
	"""
	global last_in
	global verbose
	if verbose:
		print("SAY:" + text)
	last_in = gettext(text)

	
def get(expected_in = None):
	"""
	Validate that response on the last request to Aigents is one as expected.
	Don't validate if no expected responce is provided.
	Print the response if verbose is set to True.
	Args:
		expected_in - expected response text
	Returns:
		nothing
	"""
	global last_in
	global failed
	global verbose
	if expected_in != None and expected_in != last_in:
		print("GET:\n" + last_in + "\nERROR - MUST BE:\n" + expected_in)
		failed = failed + 1
		sys.exit()
	else:
		if verbose:
			print("GET:" + last_in);


def login(name = "john", email = "john@doe.org", surname = "doe", question = "q", answer = "a"):
	"""
	Create default user and temporary session for it.
	Args:
		name - name of the session user to create the session
		email - email of the user
		surname - surname of the user
		question - password hint
		answer - password
	Returns:
		nothing
	TODO:
		have session user name identified automatically 
	"""
	say("My name "+name+", email "+email+", surname "+surname+".")
	get("What your secret question, secret answer?")
	say("My secret question "+question+", secret answer "+answer+".")
	get("What your "+question+"?")
	say("My "+question+" "+answer+".")
	get("Ok. Hello John Doe!\nMy Aigents " + version + copyright)


def logout(name = "john"):
	"""
	Destroy default user temporary session along with user.
	Args:
		name - name of the session user to destroy the session
	Returns:
		nothing
	TODO:
		have session user name identified automatically 
	"""
	say("Your trusts no " + name + ".");
	get("Ok.");	
	say("No name " + name + ".");
	get("Ok.");
	say("No there times today.");
	get("Ok.");
	say("What times today?");
	get("There not.");
	say("My logout.");
	get("Ok.");


def set_verbose(value = False):
	"""
	Set verbosity level for debugging
	Args:
		value - True to log debugging info, False to stay silent
	Returns:
		nothing
	"""
	global verbose
	verbose = value
