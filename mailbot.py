import smtplib
import json
import sys

if len(sys.argv) != 2:
	print("Incorrect number of arguments.")
	sys.exit(0)

with open(sys.argv[1]) as data_file:    
    data = json.load(data_file)

# configure server
server = smtplib.SMTP('smtp.gmail.com:587') # try to see if there's a way to send from NYU servers
variable_dictionary = {}

# populate data fields
from_address = data["from"]
username = data["username"]
password = data["password"]
raw_message = data["message"]
variable_to = data["to"]

# populate the dictionary of variables and replacers
list_length = -1
for rows in data["variables"]:
	var = rows["var"]
	list_vals = []
	for vals in rows["vals"]:
		list_vals.append(vals["val"])
	if (list_length == -1):
		list_length = len(list_vals)
	elif list_length != len(list_vals):
		print("Error: every list of variables must be of the same length.")
		sys.exit(0)
	variable_dictionary[var] = list_vals

server.ehlo()
server.starttls()
server.login(username, password)

# replace variables in the message
for i in range(0, list_length):
	message = raw_message
	to_address = list_vals[variable_to][i]
	for key, values in list_vals.iteritems():
		message = message.replace(key, values[i])

	# send the message out
	server.sendmail(from_address, to_address, message)

server.quit()