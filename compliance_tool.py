#!/usr/local/bin/env python3

"""

Script      :  compliance_tool.py

Author      :  Jonathan Booth

Description     :  Command line tool for reading compliance ini files, returning looked up enums and javascript literals

Requirements    :  Python3 ( for configparser module to be able to set (strict=False) ), the Tabulate module

"""

from optparse import OptionParser
from app.inifile import IniFile


parser = OptionParser()
parser.add_option('-f', '--file', help='takes the path of an ini FILE to parse', dest='file', action='store', type='string')
parser.add_option('-j', '--javascript_literals', help='takes FOLDER path for the Javascript literal files', dest='js_lit', action='store', type='string')
parser.add_option('-l', '--language', help='takes two character language code (default "en")', dest='language', type='string', default ='en')

opts, args = parser.parse_args()

if opts.file is None or opts.js_lit is None:
    parser.print_help()

else:
    IniFile(opts.file, opts.js_lit, opts.language)
