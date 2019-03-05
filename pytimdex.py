# pytimdex -- python tools for the TIMDEX api
#
# (c) 2019 Massachusetts Institute of Technology
#
# cc-by

import requests
import datetime

all_fields = [
        'abstract',
        'alternate_title',
        'authors',
        'available',
        'call_numbers',
        'content_format',
        'content_type',
        'doi',
        'edition',
        'full_record_link',
        'id',
        'imprint',
        'isbns',
        'issns',
        'languages',
        'lccn',
        'links',
        'notes',
        'oclcs',
        'physical_description',
        'place_of_publication',
        'publication_date',
        'publication_frequency',
        'realtime_holdings_link',
        'source_link',
        'source_link',
        'subjects',
        'summary',
        'summary_holdings',
        'title'
        ]
brief_fields = [
        'authors',
        'content_format',
        'content_type',
        'doi',
        'full_record_link',
        'id',
        'imprint',
        'isbns',
        'issns',
        'lccn',
        'links',
        'oclcs',
        'publication_date',
        'realtime_holdings_link',
        'source',
        'source_link',
        'subjects',
        'summary_holdings',
        'title'
        ]
isbd_fields = [
        'id',
        'title',
        'edition',
        'imprint',
        'physical_description',
        'notes',
        'authors',
        'subjects',
        'call_numbers',
        'isbns',
        'oclcs',
        'source_link'
        ]
urls = {'base':'https://timdex.mit.edu/api',
        'ver':'/v1',
        'auth':'/auth',
        'get':'/record/',
        'search':'/search?',
        'kw':'q=',
        'keyword':'q=',
        'ti':'q=', # title searching not yet supported so use q
        'title':'q=',
        'au':'authors=',
        'author':'authors',
        'co':'authors=',
        'contributor:':'co',
        'su':'subjects=',
        'subject':'subjects=',
        'bn':'isbns=',
        'isbn':'isbns=',
        'sn':'issns=',
        'issn':'issns=',
        'doi':'doi='}
def authenticate(email , password):
    output = ''
    auth_url = urls['base'] + urls['ver'] + urls['auth']
    print(auth_url)
    r = requests.get(auth_url, auth=(email, password))
    print(r.headers)
    print(r.text)
    if type(r.text) is str:
        output = str(r.text).replace('"','')
        return output
    else:
        return 'authentication failed'
def stringify(input,delimiter,depunctuate):
    # given a string, list, or dictionary, returns a string with all values concatenated, separated by delimiter
    input_type = type(input)
    if input_type is str:
        if depunctuate:
            output = strip_final_punct(input)
        else:
            output = input
        return output
    elif input_type is list:
        output = ''
        out_list = []
        for item in input:
            item_type = type(item)
            if item_type is str:
                if depunctuate:
                    out_list.append(strip_final_punct(item))
                else:
                    out_list.append(item)
            else:
                out_list.append(stringify(item,delimiter,depunctuate))
        for out_item in out_list:
            output += out_item
            output += delimiter
        return output[:-1]
    elif input_type is dict:
        output = ''
        out_list = []
        keys = list(input)
        for key in keys:
            output = ''
            out_list = []
            entry = input[key]
            entry_type = type(entry)
            if entry_type is str:
                out_list.append(entry)
            else:
                out_list.append(stringify(entry,delimiter,depunctuate))
        for out_item in out_list:
            output += out_item
            output += delimiter
        return output[:-1]
def strip_final_punct(input):
    puncts = [
        '.',',',
        ':',';',
        '/','=']
    if input[-1] in puncts:
        output = input[:-1]
        output = output.rstrip()
    else:
        output = input
    print(output)
    return output
class query:
    def __init__(self , token):
        self.token = token
        self.name = 'query'
        self.timestamp = str(datetime.datetime.now())
        self.queries = []
        self.results = []
        self.errors = ''
    def get(self , id , mode):
        output = True
        print('get full record')
        headers = {'Authorization': 'Bearer ' + self.token}
        URL = urls['base']+ urls['ver'] + urls['get'] + id
        print('submit url: ' + URL)
        result = requests.get(URL, headers=headers).json()
        if 'error' in result:
            output = False
            self.errors += 'error in function get_full: record not retrieved\n'
        else:
            if mode == 'a': # append results
                self.results.append(result)
            elif mode == 'r': # replace results
                self.results = []
                self.results.append(result)
            else:
                output = False
                self.errors += 'error in function get_full: incorrect mode specified (must be "a" or "r")\n'
        return output
    def get_fields(self , id, fields_to_get , mode):
        output = True
        field_list = []
        print('get specified fields')
        if type(fields_to_get) is str:
            field_list.append(fields_to_get)
        elif type(fields_to_get) is list:
            field_list.extend(fields_to_get)
        else:
            output = False
            self.errors += 'error in function get_field: fields_to_get must be STR or LIST'
            return output
        for field in field_list:
            if field not in all_fields:
                output = False
                self.errors += 'error in function get_fields: "fields" value ("' + field + '") does not match available fields'
                return output
        headers = {'Authorization': 'Bearer ' + self.token}
        URL = urls['base'] + urls['ver'] + urls['get'] + id
        result = requests.get(URL, headers=headers).json()
        if 'error' in result:
            output = False
            self.errors += 'error in function get_full: record not retrieved\n'
        else:
            result_set = []
            for key in field_list:
                new_entry = {key : result[key]}
                result_set.append(new_entry)
            if mode == 'a': # append results
                self.results.append([result_set])
            elif mode == 'r': # replace results
                self.results = []
                self.results.append([result_set])
            else:
                output = False
                self.errors += 'error in function get_full: incorrect mode specified (must be "a" or "r")\n'
        return output
    def write_results_sheet(self , filename, fields, column_headers, depunctuate):
        # writes results to file in rectangular format
        # fields = 'a' all ; 'b' brief ; 'i' isbd-like ; [list] of fields
        output = True
        out_list = []
        if fields == 'a':
            keys = all_fields
        elif fields == 'b':
            keys = brief_fields
        elif fields == 'i':
            keys = isbd_fields
        else:
            if type(fields) is str:
                if fields not in all_fields:
                    output = False
                    self.errors += 'error in function write_sheet: requested field does not exist'
                    return output
                else:
                    keys = [fields]
            elif type(fields) is list:
                keys = fields
            else:
                output = False
                self.errors += 'error in function write_sheet: "fields" must be str or list'
                return output
        if column_headers == True:
            out_list.append(keys)
        for item in self.results:
            row_to_add = []
            for key in keys:
                try:
                    val = item[key]
                except KeyError:
                    val = '<empty>'
                row_to_add.append(stringify(val,'|',depunctuate))
            out_list.append(row_to_add)

        with open(filename,'w') as file:
            for row in out_list:
                for column in row:
                    try:
                        file.write(column)
                        file.write('\t')
                    except:
                        file.write('error\t')
                file.write('\n')
        file.close()
        output = True
    def search(self,
               search_term):
        # given str 'term' and controlled value 'facet', returns timdex:ids as list
        output = []

        URL = urls['base']+urls['ver']+urls['search']
        URL += urls['kw'] + search_term.replace(' ','%20')
        headers = {'Authorization': 'Bearer ' + self.token}
        print('headers: ' + str(headers))
        print('submit URL: '+ URL)
        response = requests.request("GET", URL, headers=headers).json()
        for val in response['results']:
            output.append(val['id'])
        return output