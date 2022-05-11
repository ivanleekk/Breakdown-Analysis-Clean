from primitives import *
import re
import pandas as pd
from datetime import datetime
import pathlib
import os

path = str(pathlib.Path.cwd())


def last_pm(spreader, spreader_details):
    """# return the last date pm was done for the spreader"""
    pm_index = colummn_index("Last Completion Date", spreader_details)
    sp_index = colummn_index("Asset", spreader_details)
    for row in read_data(spreader_details):
        if row[sp_index] == spreader:
            pm_date = row[pm_index]
    result = [spreader, pm_date]
    return result


def bdn_date(event):
    """# returns the date that bdn occured"""
    return event[18]  # report date


def true_spreader(assetnum):
    """# returns if the assetnum is a random number or actual spreader code"""
    fact = re.findall("^[A-Z]", assetnum)
    if fact:
        return True
    else:
        return False


def is_spreader(assetnum):
    """# returns if the assetnum is a spreader or not"""
    fact = re.findall("[Kk][0-9][0-9][0-9]|[0-9][0-9][0-9][aAbB]", assetnum)
    if fact:
        return True
    else:
        return False


def clean_bdn(bdn_details):
    """# remove wrong spreader codes from bdn details"""
    data = bdn_details[1]
    asset_index = colummn_index("assetnum", bdn_details)
    index = 0
    indexes = []
    for event in data:
        if true_spreader(event[asset_index]):
            pass
        else:
            indexes.append(index)
        index += 1
    for index in indexes[::-1]:
        data.pop(index)
    bdn_details[1] = data
    return bdn_details


def read_event_datetime(date_time):
    """# read the datetime from csv"""
    event_date_format = "%b %d, %Y, %I:%M %p"
    event_date = datetime.strptime(date_time, event_date_format)
    return event_date


# returns a list of [assetnum, pm date, bdn date]


def pm_to_bdn(spreader_history, bdn_details):
    """# generate a list of all events and the whole history of PMS for that spreader"""
    result = []
    asset_index = colummn_index("assetnum", bdn_details)
    for event in bdn_details[1]:
        event_date_format = "%b %d, %Y, %I:%M %p"
        event_date = datetime.strptime(str(bdn_date(event)), event_date_format)
        asset = event[asset_index]
        for spreader in spreader_history:
            if spreader[0] == asset:
                result.append(spreader + [event_date])
    return result


def days_to_bdn(event):
    """# returns the number of days since pm to bdn event"""
    pm_history = event[1]
    bdn_date = event[2]
    difference = []
    for pm_date in pm_history:
        days_between = bdn_date - pm_date
        if days_between.days > 0:
            difference.append(days_between)
    if len(difference) > 0:
        most_recent_pm = min(difference)
        return most_recent_pm.days
    pass


# return a dict with a assetnum and days to all associated breakdowns


def bdn_total(pm_history, bdn_details):
    bdn_history = pm_to_bdn(pm_history, bdn_details)
    result = {}
    for event in bdn_history:
        result[event[0]] = []
    for event in bdn_history:
        days = days_to_bdn(event)
        result[event[0]].append(days)
    return result


# look for spreader codes in the description of WO


def parse_for_spreader(event, lists):
    """use regex to find Kxxx?A/B (serial of spreader)"""
    longdesc_index = colummn_index("longdesc", lists)
    longdesc = event[longdesc_index]  # string of longdesc
    spreaders = set(re.findall("[Kk][0-9][0-9][0-9]?[^. \n]", longdesc))
    if len(spreaders) > 0:
        result = list(spreaders)
        return result
    else:
        pass
    pass


def find_full_assetnum(short_form, spreader_details):
    """# link Kxxx form to full assetnum"""
    if type(short_form) == str:
        assets = read_colummn("Asset", spreader_details)
        asset = re.findall("[A-Z][A-Z][A-Z]" + short_form, str(assets))
        return str(asset)
    else:
        pass


def historical_pm(assetnum, pm_details):
    """# returns a list of a spreader with all the dates of PMS done on it"""
    pm_index = colummn_index("actfinish", pm_details)
    sp_index = colummn_index("assetnum", pm_details)
    dates = []
    for row in read_data(pm_details):
        if row[sp_index] == assetnum:
            date = read_event_datetime(row[pm_index])
            dates.append(date)

    dates.sort()
    spreader = [assetnum, dates]
    return spreader
    pass


def spreader_history(spreader_list, pm_details):
    """# returns a dict of ALL the spreaders and all the dates PMS was done on it"""
    pm_history = {}
    for spreader in read_data(spreader_list):
        pm_history[spreader] = historical_pm(spreader, pm_details)[1]
        # pm_history.append(historical_pm(spreader, pm_details))
    return pm_history


def clean_dict(bdn_days):
    """# Remove all None values from the dict"""
    for key in bdn_days.keys():
        result = []
        for x in bdn_days[key]:
            if x != None:
                result.append(x)
        bdn_days[key] = result

    temp = []
    for key in bdn_days.keys():
        if bdn_days[key] == []:
            temp.append(key)

    for key in temp:
        del bdn_days[key]


def clean_dataframe(dataframe):
    """# Remove all columns from dataframe with label "dtfordf" or "wopriority" or "lead" or "jpnum" or "parent" or "downflag" or "status" or "duration" or columns starting with "Aggregat" or starting with "Column" or starting with "sched"""
    for column in dataframe.columns:
        if (
            column == "dtfordf"
            or column == "wopriority"
            or column == "lead"
            or column == "jpnum"
            or column == "parent"
            or column == "downflag"
            or column == "status"
            or column == "duration"
            or column.startswith("Aggregat")
            or column.startswith("Column")
            or column.startswith("sched")
        ):
            dataframe.drop(column, axis=1, inplace=True)
    return dataframe


def change_problemcode(dataframe):
    """# change cells in csv in colummn "problemcode" which have value "LM" or "RY" or "SW" and replace with "LS"""
    dataframe["problemcode"] = dataframe["problemcode"].replace(
        ["LM", "RY", "SW"], "LS"
    )
    return dataframe
    pass


def split_csv(bdn_events):
    """# split csv into 2 diff sets, first one without secondary part code, second one with part code"""
    problem_code_index = colummn_index("problemcode", bdn_events)
    raw_data = read_data(bdn_events)
    top_row = read_header(bdn_events)
    blank_code = pd.DataFrame()
    coded_code = pd.DataFrame()
    for row in raw_data:
        if row[problem_code_index] == "":
            blank_code = blank_code.append(pd.DataFrame([row]), ignore_index=True)
        elif row[problem_code_index] != "":
            coded_code = coded_code.append(pd.DataFrame([row]), ignore_index=True)
    blank_code.columns = top_row
    coded_code.columns = top_row
    return blank_code, coded_code


def event_contains(keyword, events_df):
    """# returns a dataframe of all the events with the problem code and adds it to the dataframe"""
    longdesc = events_df["longdesc"]
    flag = pd.DataFrame()
    for desc in longdesc:
        if keyword.lower() in desc.lower():
            flag = pd.concat([flag, pd.DataFrame([1])], ignore_index=True)
        else:
            flag = pd.concat([flag, pd.DataFrame([0])], ignore_index=True)
    flag.columns = [f"{keyword} flag"]
    events_df = pd.concat([events_df, flag], axis=1)
    return events_df
    pass


def keywords_flag(list_of_keywords, events_df):
    """# returns a list of all the events a list of problem codes and adds it to the dataframe"""
    for word in list_of_keywords:
        events_df = event_contains(word, events_df)
    return events_df
    pass


# find correlation between rows in a dataframe


# find the appropriate tag for the event failurecode from the flags provided


def split_df(dataframe, folder):
    """# for each type of problemcode, split the dataframe into a new one and create a new dataframe with the problemcode and the flag. Place the output file into the folder specified"""
    problemcodes = set(dataframe["problemcode"])
    for code in problemcodes:
        output_df = dataframe[dataframe["problemcode"] == code]

        os.mkdir(path + r"\\" + folder + f"{code}")
        output_df.to_csv(folder + f"{code}\\" + f"{code}.csv", index=False)
    pass


def split_csv_with_choice(bdn_events, column):
    """# split csv into 2 diff sets, one coded and one blank based on column given"""
    problem_code_index = colummn_index(column, bdn_events)
    raw_data = read_data(bdn_events)
    top_row = read_header(bdn_events)
    blank_code = pd.DataFrame()
    coded_code = pd.DataFrame()
    for row in raw_data:
        if row[problem_code_index] == "":
            blank_code = blank_code.append(pd.DataFrame([row]), ignore_index=True)
        elif row[problem_code_index] != "":
            coded_code = coded_code.append(pd.DataFrame([row]), ignore_index=True)
    blank_code.columns = top_row
    coded_code.columns = top_row
    return blank_code, coded_code
