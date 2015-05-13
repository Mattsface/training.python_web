#!/usr/bin/python
import cgi
import cgitb
import json

cgitb.enable()
form = cgi.FieldStorage()
operands = form.getlist('operand')
total = 0
for operand in operands:
    try:
        value = int(operand)
    except ValueError:
        value = 0
    total += value
output = str(total)

print "Content-type: text/plain"
print "Content-Length: %s" % len(output)
print
print output
