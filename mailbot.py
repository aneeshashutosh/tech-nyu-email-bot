import smtplib
import json
import sys
import time
import mimetypes
import email
import email.mime.application
from email.mime.text import MIMEText as text

filename = ""
if len(sys.argv) < 2:
    print("Incorrect number of arguments.")
    sys.exit(0)

with open(sys.argv[1]) as data_file:
    data = json.load(data_file, strict=False)

if len(sys.argv) == 3:
    filename = sys.argv[2]


# populate data fields
from_address = data["name"]
username = data["username"]
password = data["password"]
raw_message = data["message"]
raw_subject = data["subject"]
variable_to = data["to"]
variable_dictionary = {}

# configure server
# try to see if there's a way to send from NYU servers
server = smtplib.SMTP('smtp.gmail.com', 587)
if "@nyu.edu" in username:
    server = smtplib.SMTP_SSL('smtp.nyu.edu', 465)

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
    subject = raw_subject
    to_address = variable_dictionary[variable_to][i]
    sys.stdout.write("Sending email to " + to_address + "... ")
    for key, values in variable_dictionary.iteritems():
        message = message.replace(key, values[i])
        subject = subject.replace(key, values[i])

    msg = email.mime.Multipart.MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_address
    msg['To'] = to_address
    body = email.mime.Text.MIMEText(message)
    msg.attach(body)


    if (filename != ""):
        fp = open(filename,'rb')
        att = email.mime.application.MIMEApplication(fp.read(), _subtype="pdf")
        fp.close()
        att.add_header('Content-Disposition', 'attachment', filename = filename)
        msg.attach(att)

    # send the message out
    server.sendmail(from_address, to_address, msg.as_string())
    time.sleep(15)
    sys.stdout.write("Done!\n")

server.quit()
