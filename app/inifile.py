#!/usr/bin/python3

import re
import configparser
from tabulate import tabulate
from app.enums import enum_type_fix, enums_dict
import collections
from app.jsliterallookup import JsLookup
import os


class IniFile(object):

    def __init__(self, file_path, js_literals_path, language_code="en"):

        self.file_path = file_path
        self.js_literals_path = js_literals_path
        self.js_files_list = []
        self.language_code = language_code
        for i in (next(os.walk(self.js_literals_path))[2]):
            self.js_files_list.append(self.js_literals_path + "/" + i)

        self.config = configparser.ConfigParser(strict=False)

        try:
            self.config.read(self.file_path)
        except configparser.ParsingError:  # allows reading of upos1.ini files without parsing for key value pairs
            print("Extracting includes from upos1.ini")
            pass

        self.conditional_list = []
        self.conditional_value = ""
        self.value_dictionary = collections.OrderedDict()

        self._include_check()
        self.file_type = self._get_file_type()
        if self.file_type == "upos1":  # upos1.ini configs are not in the same enum format as compliance configs
            pass
        else:
            self._get_conditional_list()
            self._get_key_value_pairs()
            self._lookup_enums_and_js()
            self._make_table()

    def _include_check(self):

        file = open(self.file_path, "r")
        for line in file.readlines():
            if "!include" and "compliance" in line:
                include_filename = line.strip("!include").strip("\n").strip(" ")
                discard_portion = re.findall(r"([a-z0-9_]*.ini)", str(self.file_path))
                stripped_file_path = self.file_path.replace(discard_portion[0], "")
                include_filepath = stripped_file_path + include_filename

                IniFile(include_filepath, self.js_literals_path, self.language_code)

    def _get_file_type(self):  # extracts file type (product/charge/compliance/qualifier) from filename

        result = re.findall(r"([a-z]*)_([a-z]*)", self.file_path)

        try:
            if result[0][0] == "qalifier":  # handles mis-spelt "qalifier_compliance.ini" files such as TUI's
                return "qualifier"
            else:
                return result[0][1]
        except IndexError:
            return "upos1"

    def _get_conditional_list(self):
        try:
            self.seller_name = (re.findall(r"[^_]*", self.config.sections()[1]))[0]
        except IndexError:
            self.seller_name = (re.findall(r"[^_]*", self.config.sections()[0]))[0]

        self.conditional_value = (self.seller_name + "_" + self.file_type).upper()
        if self.file_type in ["product", "qualifier", "charge"]:
            self.conditional_value += "S"

        for section in self.config.sections():
            if section in self.conditional_value:
                for key, value in self.config.items(self.conditional_value):
                    if key == "use_turnover":  # To prevent USE_TURNOVER from being counted as a conditional value
                        pass
                    else:
                        self.conditional_list.append(value)

    def _get_key_value_pairs(self):

        i = 1
        for value in self.conditional_list:
            self.value_dictionary[value] = self.config.items(self.conditional_value + "_{}".format(i))
            i += 1

        # convert key/value tuples to lists
        for key in self.value_dictionary:
            for i in range(0, 30):
                try:
                    self.value_dictionary[key][i] = list(self.value_dictionary[key][i])
                except IndexError:
                    pass

    def _lookup_enums_and_js(self):

        js_lookup_object = (JsLookup(self.js_files_list))

        for key in self.value_dictionary:
            for data_list in self.value_dictionary[key]:

                try:
                    data_list.append(enums_dict[enum_type_fix(data_list[1])])
                except KeyError:
                    data_list.append("N/A")
                except ValueError:
                    data_list.append("N/A")
                try:
                    data_list.append(js_lookup_object.literal_dictionary[self.language_code][data_list[2]])
                except KeyError:
                    data_list.append("N/A")

    def _make_table(self):

        headers = ("Key", "Value", "Database Field", "What Customer Sees")
        print("\nFilename = ", self.file_path)
        print("Seller = ", self.seller_name)
        for key in self.value_dictionary:
            print("\n[", self.file_type, ": ", key, "]")
            print(tabulate(self.value_dictionary[key], headers=headers, tablefmt="simple", numalign="left"))
