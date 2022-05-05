from traceback import print_tb
from auto_learner import *

"""used to check accuracy of trained data on test set not seen before"""
# data directory
data_folder = r"Current Data\\"

# read data to use in model
model_1 = pd.read_csv(data_folder + "model.csv")
test_dict = eval(model_1.iloc[0]["weights"])
test_data = pd.read_csv(data_folder + "test_data.csv")

# run model
after = model(
    test_data,
    test_dict,
    model_1.iloc[0]["threshold"],
    tester=False,
)

# output results to test_results.csv
after.to_csv(data_folder + "test_results.csv", index=False)
