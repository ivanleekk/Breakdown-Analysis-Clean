from traceback import print_tb
from auto_learner import *

# data directory
data_folder = r"Current Data\\"

# read data
model_1 = pd.read_csv(data_folder + "model.csv")
bdn = clean_dataframe(pd.read_csv(data_folder + "ALL SP BDN.csv"))
test_dict = eval(model_1.iloc[0]["weights"])
spreader_details = read_file(data_folder + "Spreader details.csv")
pm_details = read_file(data_folder + "Spreader_PM_2019-2022.csv")

# classify data
after = model(
    bdn,
    test_dict,
    model_1.iloc[0]["threshold"],
    tester=False,
)

after.to_csv(data_folder + "save.csv", index=False)

# get pm history of spreaders
spreader_list = read_colummn("Asset", spreader_details)
pm_history = spreader_history(spreader_list, pm_details)
print(pm_history)
# for every row in the after dataframe, check to see if assetnum is valid and if it is, find the last pm date
# and the number of days from pm to bdn and add it to the dataframe
days_list = []
for index, row in after.iterrows():
    if row["assetnum"] in pm_history.keys() and pm_history[row["assetnum"]] != []:
        temp = []
        for i in pm_history[row["assetnum"]]:
            temp.append((read_event_datetime(row["reportdate"]) - i).days)
        temp = list(filter(lambda x: x > 0, temp))
        if temp == []:
            day = None
        else:
            day = min(temp)
        days_list.append(day)
    else:
        days_list.append(None)

after["days since PM"] = days_list

# if assetnum is not a spreader, replace with "assetnum not known"
after["assetnum"] = after["assetnum"].apply(
    lambda x: "assetnum not known" if x not in spreader_list[1] else x
)

# output dataframe to all_bdn.csv
after.to_csv(data_folder + "all_bdn.csv", index=False)
