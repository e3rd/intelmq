#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generates a SQL command file with commands to create the events table.

Reads the Data-Harmonization.md document from
`/opt/intelmq/docs/Data-Harmonization.md` and generates an SQL command from it.
The SQL file is saved in `/tmp/initdb.sql`.
"""
from __future__ import print_function, unicode_literals
import json
import sys

from intelmq import HARMONIZATION_CONF_FILE

OUTPUTFILE = "/tmp/initdb.sql"
FIELDS = dict()

try:
    print("INFO - Reading %s file" % HARMONIZATION_CONF_FILE)
    with open(HARMONIZATION_CONF_FILE, 'r') as fp:
        DATA = json.load(fp)['event']
except IOError:
    print("ERROR - Could not find %s" % HARMONIZATION_CONF_FILE)
    print("ERROR - Make sure that you have intelmq installed.")
    sys.exit(-1)

for field in DATA.keys():
    value = DATA[field]

    if value['type'] in ('String', 'Base64', 'URL', 'FQDN'):
        dbtype = 'varchar({})'.format(value.get('length', 2000))
    elif value['type'] in ('IPAddress', 'IPNetwork'):
        dbtype = 'inet'
    elif value['type'] == 'DateTime':
        dbtype = 'timestamp with time zone'
    elif value['type'] == 'Boolean':
        dbtype = 'boolean'
    elif value['type'] == 'Integer':
        dbtype = 'integer'
    elif value['type'] == 'Float':
        dbtype = 'real'
    elif value['type'] == 'UUID':
        dbtype = 'UUID'
    else:
        print('Unknow type {!r}, assuming varchar(2000) by default'
              ''.format(value['type']))
        dbtype = 'varchar(2000)'

    FIELDS[field] = dbtype

    # TODO: ClassificationType
    # TODO: MalwareName

initdb = """CREATE table events (
    "id" BIGSERIAL UNIQUE PRIMARY KEY,"""
for field, field_type in sorted(FIELDS.items()):
    initdb += '\n    "{name}" {type},'.format(name=field, type=field_type)

print(initdb[-1])
initdb = initdb[:-1]
initdb += "\n);"

with open(OUTPUTFILE, 'w') as fp:
    print("INFO - Writing %s file" % OUTPUTFILE)
    fp.write(initdb)
