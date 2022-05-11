import csv
import pathlib


def read_file(filename):  # read csv file
    with open(filename, "r", encoding="utf8") as file:
        details = csv.reader(file)
        header = []
        header = next(details)
        data = []
        for info in details:
            data.append(info)
    info = [header, data]
    return info


def read_header(list):  # return header of file
    return list[0]


def read_data(list):  # return body of file
    return list[1]


def colummn_index(name, list):  # return the index of that header in a file
    header = read_header(list)
    index = 0
    for head in header:
        if head == name:
            break
        else:
            index += 1
    return index


def read_colummn(name, list):  # return the whole colummn based on its header name
    index = colummn_index(name, list)
    temp = []
    data = read_data(list)
    for row in data:
        temp.append(row[index])
    result = [name, temp]
    return result


# flatten a list recursively


def flatten_list(l):
    if isinstance(l, list):
        return sum(map(flatten_list, l), [])
    else:
        return [l]
