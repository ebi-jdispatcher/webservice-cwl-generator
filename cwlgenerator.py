#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import sys
import requests
import configparser
import xml.etree.ElementTree as ET
from jinja2 import Environment, FileSystemLoader
import easyargs
import xmltodict


# Wrapper for a REST (HTTP GET) request
def restRequest(url):
    return requests.get(url).text


def escape(string):
    return " ".join(string.replace('\r\n', ' ').replace('\r', ' ').
                    replace('\n', ' ').replace('\t', ' ').strip().split())


def tool_from(url):
    response = restRequest(url)
    description = escape(ET.fromstring(response).text)
    return description, parameters_of(url)


def parameters_of(url):
    response = restRequest(url + u'/parameters')
    params = ET.fromstring(response)
    return {param.text: details_of(url, param.text) for param in params}


def details_of(url, param_name):
    response = restRequest(url + u'/parameterdetails/' + param_name)
    details = ET.fromstring(response)
    values = {detail.tag: detail.text for detail in details}

    default_values = {'protein': [], 'nucleotide': [], 'vector': [], 'generic': []}
    if param_name != "stype":
        param = xmltodict.parse(response)
        for key, val in param['parameter'].items():
            if key == "values":
                if 'value' in param['parameter']['values']:
                    # loop over list of values
                    for value in param['parameter']['values']['value']:

                        # checks if key=context and key=defaultValueContexts exists
                        if 'properties' in value:
                            if 'property' in value['properties']:
                                # loop over list of properties
                                prop = value['properties']['property']
                                if type(prop) is list:
                                    for pro in prop:
                                        if 'key' in pro and 'value' in pro:
                                            if pro['key'] == 'defaultValueContexts' and 'value' in value:
                                                # all contexts == same as defaultValue
                                                for key in ["protein", "nucleotide", "vector"]:
                                                    if key in pro['value']:
                                                        default_values[key].append(value['value'])

                        # else try find generic 'defaultValue'
                        if 'defaultValue' in value and 'value' in value:
                            if value['defaultValue'] == 'true':
                                default_values['generic'].append(value['value'])
    values["default_values"] = default_values
    return values


def get_cwl_inputs(name, parameter, position):

    position += 1
    label = parameter['name']
    doc = parameter['description']
    default = ",".join(parameter['default_values']['generic'])
    typer = "string?"
    string = '''\
  %s:
    type: %s
    label: %s
    doc: "%s"
    inputBinding:
      prefix: --%s
      position: %i
''' % (name, typer, label, doc, name, position)
    if default != "":
        string += '    default: "%s"\n' % default
    return string, position


def generate_client(tool, template):
    return template.render(tool=tool) + "\n"


def write_client(filename, contents, dir="dist"):
    if not os.path.isdir(dir):
        os.mkdir(dir)
    with open(os.path.join(dir, filename), 'w') as fh:
        if sys.version_info.major < 3:
            fh.write(contents.encode('ascii', 'ignore').decode('ascii'))
        else:
            fh.write(contents.encode('utf-8', 'ignore').decode('utf-8'))


@easyargs
def main(lang, docker=False, client="all",
         baseurl="https://www.ebi.ac.uk/Tools/services/rest/"):
    """Generates CWLS to use with 'Python', 'Perl' or 'Java' clients and Docker"""

    language = lang.lower().split(",")
    client = client.lower().split(",")
    required_params = ["sequence", "asequence", "bsequence",
                       "email", "program", "stype", "database"]

    twoseqs = ["emboss_needle", "emboss_stretcher", "emboss_water",
               "emboss_matcher", "lalign", "genewise", "emboss_dotmatcher",
               "emboss_dotpath", "emboss_dottup", "promoterwise", "wise2dba"]

    # CWL files
    template = Environment(loader=FileSystemLoader(u'.')) \
        .get_template(os.path.join('templates', 'cwl', 'client.cwl.j2'))

    parser = configparser.ConfigParser()
    parser.read(u'clients.ini')
    for lang in language:
        if lang == "python":
            lang_ext = "py"
        elif lang == "perl":
            lang_ext = "pl"
        else:
            print("%s not yet implemented..." % lang)
            return
        for idtool in parser.keys():
            if "all" in client or idtool in client:
                if idtool == u'DEFAULT':
                    continue
                tool = {u'id': idtool,
                        u'url': u'{}{}'.format(baseurl, idtool),
                        u'filename': u'{}.cwl'.format(idtool),
                        u'lang': lang,
                        u'lang_ext': lang_ext,
                        u'inputs_req': [],
                        u'inputs_opt': [],
                        u'outputs': [],
                        }
                tool[u'description'], parameters = tool_from(tool[u'url'])

                if docker:
                    tool[u'docker'] = True

                for option in parser[idtool]:
                    tool[option] = parser.get(idtool, option)

                inputs_req, inputs_opt, outputs = [], [], []

                position = 8
                if idtool in twoseqs:
                    position = 9
                for (name, parameter) in parameters.items():
                    if "sequence" not in name:
                        string, position = get_cwl_inputs(name, parameter, position)
                        inputs_opt.append(string)

                tool[u'inputs_req'] = "\n".join(inputs_req)
                tool[u'inputs_opt'] = "\n".join(inputs_opt)
                tool[u'outputs'] = "\n".join(outputs)
                contents = generate_client(tool, template)
                write_client(tool[u'filename'], contents)
                print("Generated CWL for %s" % tool['url'])


if __name__ == u'__main__':
    main()
