# import
import pytimdex as pt
import csv
import secrets as s

# open file & build id list:
def read_file(filename='input.txt'):
    file_contents = []
    with open(filename, 'r') as f:
        read = csv.reader(f, delimiter='\t')
        for row in read:
            file_contents.append(row)
    return file_contents

def write_to_cache(filename, row):
    ''' adds row to cache; if cache reaches limit, writes to file <filename> and clears cache

    :param row:list
    '''
    cache_data.append(row)
    counter = len(cache_data)

    while counter < cache_limit:
        print('cache size: ' + str(counter))
        print(cache_data)
        return 'adding to cache ...'
    else:
        append_to_file(filename, cache_data)
        print(cache_data)
        cache_data.clear()
        return 'writing to file ...'


def append_to_file(filename, table_to_write):
    print(table_to_write)
    with open(filename, 'a', encoding='latin-1') as f:
        for row in table_to_write:
            print(row)
            for column in row:
                try:
                    print(column)
                    f.write(column)
                except UnicodeEncodeError:
                    print('\t\terror!')
                    for char in column:
                        try:
                            f.write(char)
                        except UnicodeEncodeError:
                            f.write('!')
                finally:
                    f.write('\t')
            f.write('\n')
    f.close()
    return True


def write_to_file(filename, table_to_write):
    with open(filename, 'w', encoding='latin-1') as f:
        for row in table_to_write:
            for column in row:
                try:
                    f.write(column)
                except UnicodeEncodeError:
                    for char in column:
                        try:
                            f.write(char)
                        except UnicodeEncodeError:
                            f.write('!')
                finally:
                    f.write('\t')
        f.write('\n')

    f.close()
    return True

def try_to_add(record, output_field):
    out = ''
    try:
        if type(output_field) is str:
            out = record[output_field]

        elif type(output_field) is list:

            field_len = len(output_field)

            if field_len == 2:

                if output_field[1] == '*':
                    try:
                        for x in record[output_field[0]]:
                            out += pt.strip_final_punct(x)
                            out += '|'
                    except TypeError:
                        out = str(output_field[0]) + ' not in record'
                else:
                    out = record[output_field[0]][output_field[1]]

            elif field_len == 3:
                try:
                    out = record[output_field[0]][output_field[1]][output_field[2]]
                except TypeError:
                    out = 'error'
            else:
                out = 'invalid field request'
    except KeyError:
            out = (
                (output_field if type(output_field) is str else output_field[0])
                + ' not in record'
            )

    try:
        out = pt.strip_final_punct(out)
    except IndexError:
        pass

    return out

# script begins
#
# globals, etc
cache_data = []
cache_limit = 500
ids = read_file('input.txt')

# create td object
token = pt.authenticate(**s.timdex_keys)
q = pt.query(token)
output_table = []
output_fields = ['id', 'title', ['imprint',0], ['oclcs', '*'], ['summary_holdings', 0, 'call_number'], ['subjects','*'],
                 'source_link']


# write headers
write_to_file('output.txt', table_to_write=[['barton id', 'title', 'imprint', 'oclc id', 'call number', 'subjects',
                'barton URL']])

# write records
for count, id in enumerate(ids):
    print('\t\trecord ' + str(count))
    print('-------------------------------------------')
    record = q.get(id, 'r')

    if record == False:
        print('>> record ' + str(id) + ' not in Timdex')
    else:
        row_to_add = []
        for field in output_fields:
            row_to_add.append(try_to_add(record, field))

        print('add row:')
        print(row_to_add)
        print(write_to_cache('output.txt', row_to_add))
        print('-------------------------------------------')
        print('-------------------------------------------')

# write remainder of cache
print('writing remainder of cache')
append_to_file('output.txt', cache_data)
