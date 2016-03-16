import re


class JsLookup(object):

    def __init__(self, js_file_list):

        self.literal_dictionary = {
                                  "en": {},
                                  "ce": {},
                                  "cf": {},
                                  "de": {},
                                  "es": {},
                                  "fr": {},
                                  "it": {},
                                  "jp": {},
                                  "pt": {},
                                  "us": {}
                                  }

        for i in js_file_list:
            file = open(i, "r")

            self._build_js_literal_dict(i, file)

    def _build_js_literal_dict(self, file_name, file):

        try:
            for line in file:

                language_code = re.findall(r"^([a-z]*)", line)

                if "override" in file_name:
                    regex_enum = (re.findall(r"(?<=customer\.1\.)\D.*?(?='])", line))
                    if regex_enum == []:  # To ensure that AD0-AD4 enum fields are captured, "additional" not "customer"
                        regex_enum = (re.findall(r"(?<=additional.)\D.*?(?='])", line))

                if "override" not in file_name:
                    regex_enum = (re.findall(r"(?<=customer.)\D.*?(?='])", line))
                    if regex_enum == []:  # To ensure that AD0-AD4 enum fields are captured, "additional" not "customer"
                        regex_enum = (re.findall(r"(?<=additional.)\D.*?(?='])", line))

                regex_literal = (re.findall(r"(?<== ')(.*)(?=\';)", line))

                try:
                    self.literal_dictionary[(language_code[0])][regex_enum[0]] = regex_literal[0]
                except IndexError:
                    pass

        except UnicodeDecodeError:
            pass

