from auto_learner import *

# data directory
data_folder = r"Current Data\\"

# read raw data
bdn_details = read_file(data_folder + "All SP BDN.csv")

# split file into 2, one with problemcode and the other without
not_coded, coded = split_csv_with_choice(bdn_details, "problemcode")


# clean dataframes
not_coded = clean_dataframe(not_coded)
coded = clean_dataframe(coded)


# export dataframes to csv
not_coded.to_csv(data_folder + "not_coded.csv", index=False)
coded.to_csv(data_folder + "coded.csv", index=False)


# from the coded data, sample 80 percent of the data and use that to train the model and remainding 30 percent to test the model
training_data = coded.sample(frac=0.8)
test_data = coded.drop(training_data.index)

# save training and test data separately for use later by the tester
training_data.to_csv(data_folder + "training_data.csv", index=False)
test_data.to_csv(data_folder + "test_data.csv", index=False)


# run the trainer
trainer(training_data, num_trials=40, num_iterations=3000)
