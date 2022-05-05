from read_data import *
from random import random
from nltk import WordNetLemmatizer
from copy import deepcopy

"""# take in all the raw data and split into coded and uncoded data"""
# data directory
data_folder = r"Current Data\\"


# from the longdesc in the training data, make a dict of all the words that will appear for each problemcode and put that in a dictionary except OT
# import these modules
def make_training_dict(training_data):  # makes the training dictionary
    training_dict = {}
    lemmatizer = WordNetLemmatizer()
    stop_words = set(
        pd.read_csv(data_folder + "stop_words.csv")["stop_words"].to_list()
    )
    for (
        index,
        row,
    ) in training_data.iterrows():  # to iterate through all the rows in training data
        if row["problemcode"] == "OT":  # ignore OT codes
            continue
        elif (
            row["problemcode"] not in training_dict.keys()
        ):  # if code does not have a key yet, make one
            training_dict[row["problemcode"]] = {}
        tokens = (
            row["longdesc"]
        ).split()  # separate the desc into individual words/tokens
        for token in tokens:
            if is_spreader(token):  # ignore spreader codes
                continue
            lemmed = lemmatizer.lemmatize(token).lower()
            if (
                lemmed not in training_dict[row["problemcode"]].keys()
                and lemmed not in stop_words
            ):  # only look for words which have not appeared yet and are not in the stop_words file
                training_dict[row["problemcode"]][
                    lemmed
                ] = None  # initialise the value as None
    return training_dict


# define the model, where it will take in a dataframe and a dict of words and return a score where score is percentage of predicted codes which are the same as original codes
def model(
    data, training_dict, threshold=None, tester=True, iteration=0
):  # takes in dataframe , dict, threshold = None by default, and tester = True by default
    def get_key_from_score(val):  # inner function to find the key from its value
        for key, value in score.items():
            if val == value:
                return key

    if threshold == None:  # to create the first threshold value if none is provided
        threshold = 100 * random()
    if (
        tester == True and iteration >= 1
    ):  # if this model is part of a tester, give a variation of the threshold to let it explore, with higher iterations, threshold varies less, allowing the weights to optimise for this threshold
        threshold += (100 / iteration) * (random() - 0.5)
    if (
        tester == True
    ):  # create a deep copy of the training dict so that the next few iterations are unaffected by changes made within this function
        modified_dict = deepcopy(training_dict)
    else:  # since its not part of a tester, this will only be used once and no copy has to be made
        modified_dict = training_dict

    if (
        tester == True and iteration == 0
    ):  # for tester first iteration, since the dict will only contain None values, initialise them using a random number generator
        for key, value in modified_dict.items():
            for word, weight in value.items():
                value[word] = 10 * random()

    if (
        tester == True and iteration >= 1
    ):  # for tester after the first iteration, vary the weights by an amount to let it explore
        for key, value in modified_dict.items():
            for word, weight in value.items():
                modified_dict[key][word] += 10 * random() - 5
                if modified_dict[key][word] < 0:
                    modified_dict[key][word] = 0
    result = pd.DataFrame()
    correct = 0
    times = 0
    lemmatizer = WordNetLemmatizer()
    for index, row in data.iterrows():  # iterate through every row in the data
        score = {}  # reset score for new row
        for (
            code
        ) in (
            modified_dict.keys()
        ):  # for every code in the training dict pass through 1 time to give it a score
            score[code] = 1  # initialize score to 1
            for word in (
                row["longdesc"]
            ).split():  # split all the words in the description and iterte through all the words
                lemmed = lemmatizer.lemmatize(word).lower()  # make them all lower case
                if (
                    lemmed in modified_dict[code].keys()
                ):  # if the word is in the dictionary, multiply the code score by the weight
                    score[code] *= modified_dict[code][lemmed]
        max_score = max(score.values())  # find the higest score
        if (
            max_score > threshold
        ):  # if the higest score is above the threshold, make that code the new code for the event, if not use OT
            row["new code"] = get_key_from_score(max_score)
        else:
            row["new code"] = "OT"

        times += 1  # count the number of times the loop has run
        if row["new code"] == row["problemcode"]:
            correct += 1  # count the number of times the loop is correct
        if tester == False:  # add the entire row into the output dataframe
            result = result.append(row)
    if tester == True:  # add the relevant items into the dataframe for tester to use
        info = pd.DataFrame(
            {
                "score": [
                    correct / times,
                ],
                "weights": [
                    modified_dict,
                ],
                "threshold": [
                    threshold,
                ],
            }
        )
        return info  # returns a dataframe to be appended to the outer function if tester == True
    else:
        print(f"{100*correct/times}% accuracy")
        return result  # returns the whole dataframe if tester == False


# define the trainer which will take in data, number of trials, number of iterations per trial and return a dataframe with the model and scores
def trainer(data, num_trials, num_iterations, training_dict=None, threshold=None):
    thres = threshold
    if training_dict == None:  # if there is no dictionary, make a new one
        training_dict = make_training_dict(data)
    for i in range(num_trials):  # for the number of trials to conduct
        # print number of keywords checked in the weights
        length = 0
        for code in training_dict.keys():
            length += len(training_dict[code])
        print("Number of keywords:", length)
        test_info = pd.DataFrame(
            columns=["score", "weights", "threshold"]
        )  # create the dataframe to hold the info for this trial
        print(f"starting trial {i+1}")
        for j in range(num_iterations):  # for the number of iterations within a trial
            if (j + 1) % 50 == 0:
                print("iteration:", j + 1)
            test_info = test_info.append(
                model(data, training_dict, threshold=thres, iteration=i),
                ignore_index=True,
            )  # add a result to the trial info

        # get top 5% of trials and average out the weights and threshold
        top_10 = pd.DataFrame()  # reset top_10
        print(f"trial {i+1} complete")
        top_10 = test_info.sort_values(by="score", ascending=False).head(
            num_iterations // 20
        )
        print(top_10)
        # after running every iteration, take the top 10% of the scores and average them to get the base score for the next model
        top_10.to_csv(data_folder + f"trial_{i+1}.csv", index=False)

        # make the keys of the dict inside weights the columns of a new dataframe
        code_weights = pd.DataFrame(columns=top_10.iloc[0]["weights"].keys())
        temp = pd.DataFrame(columns=top_10.iloc[0]["weights"].keys())

        print(f"finding new weights for trial {i+2}")
        for index, row in top_10.iterrows():
            code_weights = code_weights.append(
                pd.DataFrame([row["weights"]], columns=row["weights"].keys()),
                ignore_index=True,
            )  # add the weights into the dataframe to be split

        for (
            col
        ) in (
            code_weights.columns
        ):  # every code has its own column containing the dictionaries within it
            indiv_weights = pd.DataFrame(columns=code_weights[col].iloc[0].keys())
            for colrow in code_weights[
                col
            ]:  # to unpack every dictionary used into their keys and values
                dicto = pd.DataFrame(colrow, index=[0])
                indiv_weights = indiv_weights.append(dicto, ignore_index=True)
            new_weights = pd.DataFrame(
                indiv_weights.mean(axis=0)
            )  # find average of all weights
            # remove irrelevant weights, i.e those that have a weight < 4
            new_weights = new_weights[new_weights[0] > 4]
            # transpose the dataframe to allow it to convert into dict
            new_weights = new_weights.transpose(copy=True)

            # convert the new weights for each code into a column in the temp dataframe
            new_weights = new_weights.iloc[0].to_dict()
            temp[col] = [new_weights]
        # find a new threshold for the next trial
        thres = pd.DataFrame(top_10["threshold"])
        thres = thres.mean(axis=0)[0]
        # convert the temp dataframe into the training dictionary for the next trial
        training_dict = temp.iloc[0].to_dict()
        print("new weights found")
    # add the final results into a dataframe to be exported as csv
    result = pd.DataFrame({"weights": [training_dict], "threshold": thres})
    print(result)
    result.to_csv(data_folder + "model.csv", index=False)
    return training_dict, thres
