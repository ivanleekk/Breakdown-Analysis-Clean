## Dependencies
IMPORTANT NOTE: Install the following libraries in order for this code to work.
1) nltk
2) random
3) copy
4) re
5) pandas
6) datetime
7) pathlib
8) os
9) csv

## Usage
IMPORTANT NOTE: Run all scripts from the main folder as the scripts have to access data within the "Current Data" folder.

### Model Training
In order to use this, download the following sets of data:
1) Breakdown records for the time frame to be analysed
2) List of spreader assets
3) Spreader PM Records for the relevant period

Once downloaded, move these 3 files into the "Current Data" folder.

For instructions on how to download these 3 sets of data, refer to the slides at the end of Breakdown analysis flowchart.pptx

If no model has been created, or a new model has to be trained, go to the run_auto_learner.py file and modify the string in line 7 to the name of your breakdown records file.
Adjust the fraction of data to be used as training data if needed.

Once a model has been created, it is saved as model.csv inside the "Current Data" folder.

### Normal Use
To use the model to classify the data, open the run_with_output.py file and modify the following:

1) bdn file so that it matches the name of your breakdown records file
2) spreader_details to your spreader details
3) pm_details to your PM details.

After running the script, the new code assigned to it is saved in the "new code" column and the number of days since PM will be stored in the "days since PM" column

Once done, open up the breakdown analysis Power BI dashboard and press refresh to view the new data.

## Main Files
### Auto_learner.py
The main module containing the algorithm to run the model.
Data_folder is the relative directory where the information is all stored.

#### Make_training_dict(training_data, column_to_code, info_for_coding)
    Training_data is a pandas dataframe of the coded data downloaded from Maximo

    Column_to_code is a string containing the name of the column in the csv which you want the model to train for, e.g. to train for secondary part code, key in “longdesc” Default value is “longdesc” if nothing is keyed in

    Info_for_coding is a string containing the text to be analysed in order to decide what code to use in column_to_code. E.g. you want to use the long description to decide what is the secondary part code, key in “longdesc” which is the name of the long description column in the csv. Default value is “longdesc”

What the function does is take in all the text in every row of info_for_coding and the code in column_to_code, making every word that appears a keyword in the dictionary.

Column_to_code | Info_for_coding \
LS | Operator reported that limit switch broke\
OH | QCO reported that E-OH frame stop


The data structure generated from the above data will be a dictionary of problemcodes, each containing a dictionary of the keywords contained within them, with value initialised as None. 

    {“LS”:{“Operator”: None, “report”: None, “that”: None, “limit”: None, “switch”: None, “broke”: None}, “OH”: {“QCO”: None, “report”: None, “that”: None, “E-OH”: None, “frame”: None, “stop”: None}}

As can be seen above, words that appear in multiple codes will be repeated in the whole training_dict, however within the dictionary for individual codes, there will be no repeated words.


Output of the function is the training_dict generated.
##### Lemmatisation
If you look closely at the keywords and compare them to the raw data, reported has been shortened to its base form report. Why is that so?
As part of the process to generate the keywords, a process known as lemmatisation is used to reduce all words to their base form in order to preserve their meaning and be applicable to any word which has the same base form. 

    Playing --> Play, Played --> Play, Plays --> Play

#### Model(data, training_dict, threshold, tester, iteration, column_to_code, info_for_coding, output_column)
This function is the one that will code the column_to_code based on the info_for_coding in the data provided

    Data is the dataframe of the info which has to be coded and can be downloaded from Maximo

    Training_dict is the training_dict generated from make_training_dict, or a dataframe made in a similar manner

    Threshold is an optional parameter to define what score and below should be classified as “OT”, if None is provided, a random one from 0 to 100 is generated. Default value is None
    
    Tester is an optional parameter to determine the flow of the function. If True is provided, the function will randomise the weights of every keyword in the training_dict by +-5. Output of the function will become a dataframe with 3 columns, (“score”, “weights”, “threshold”), containing these 3 respective information. If False, then function will use the training_dict as provided with no modification and the output will just be the original data with an added column with the new code inside. Default value is True
    
    Iteration is a count on the number of times it is run. If iteration is 0 and tester is True, the weights in the training_dict will be randomized in a range of 0 to 10, else if iteration >=1, they will only be randomized by +-5. Similarly, the threshold is randomized with every iteration, but the change is reduced with every successive iteration.
    
    Column_to_code is a string containing the name of the column in the csv which you want the model to train for, e.g. to train for secondary part code, key in “longdesc”. Default value is “longdesc” if nothing is keyed in
    
    Info_for_coding is a string containing the text to be analysed in order to decide what code to use in column_to_code. E.g. you want to use the long description to decide what is the secondary part code, key in “longdesc” which is the name of the long description column in the csv. Default value is “longdesc”
    
    Output_column is the name of the column with the new code, default value is “predicted code”
The way this function works is that every time it looks at a new WO, it initialises a score of 1 for every code in the training dictionary. It then looks at the string in info_for_coding and for every word that appears, it checks if that word is in the dictionary and if so, multiply the score by the respective weight.

Since scores and dictionaries for every code are separate, the score for each code is independent of each other. Once the whole string has been parsed, find the maximum score and if it is above the threshold, add a column and change the value to the code with the highest score, if not code it as “OT”.

As stated above, if tester is True, then the output of the function is a dataframe with 3 columns containing the (“score”, “weights”, “threshold”). Else if tester is False, then the output is the original data with an additional column with the name of the output_column and containing the code which the model has chosen.

#### Trainer(data, num_trials, num_iterations, training_dict, threshold, column_to_code, info_for_coding, output_file)
	Data is the raw data downloaded from maximo
	Num_trials is the number of trials to be run
    Num_iterations is the number of iterations per trial
    
    Training_dict is the training dict to be used, if None is provided, one will be generated from the data for you, default value is None
    
    Threshold is the threshold to be provided into the model function. If None is provided, then the model function will generate one for you.
    
    Column_to_code is the same as in the model function, Default value is “problemcode”
    
    Info_for coding is the same as in the model function. Default value is “longdesc”
    
    Output_file is the name of the file containing the weights to be generated at the end of the function. Default value is “model.csv”

What the function does is store all the outputs from the model function with tester = True in a dataframe and keep the top 5% of scores to find the average weight of each keyword and use that as the basis for the next trial. The average threshold of these scores is also carried forward to be used as the starting point for the next trial. 

To allow you to restart from any point in the event of PC shutting down etc, the top 5% of scores are saved in csv file named “model trial x” where x in the trial where it was generated.

To reduce size of the dictionary as it impacts speed, if the average weights are <=4, they are deemed insignificant to the final score and removed from the dictionary in the next trial.
4 is an arbitrary number and can be changed in the source code at line 213 of the auto_learner.py module.

At the end, a csv containing the weights and threshold is generated at the end of the function named as by default as "model.csv" is saved in the "Current Data" folder. Within the script, it returns the final training_dict and the threshold.

### Run_auto_learner.py
This script runs the trainer defined in the auto_learner.py module to train the model.

    Bdn_details is the raw data from the csv downloaded from Maximo
    
    Split_csv_with_choice takes in bdn_details and splits it based on if the column provided is coded or not, giving 2 dataframes as outputs, first one not_coded, second one coded.
    
    Clean_dataframe takes in the dataframe and removes unnecessary columns to speed up computation
    
    Training_data is a 80% sample of the coded data and test_data is the remainder of the coded data
Run trainer with whatever settings you want to use, from experimentation, after 50-60 trials there are diminishing returns. However that may vary with iterations used per trial. Time taken to run 200 trials of 2000 iterations took about 2 days and for 40 trials with 3000 iterations it took around 16 hours on a laptop, so use this to estimate how long you can let it run for.

### Run_with_output.py
This script is what runs the final trained model on the raw data downloaded from Maximo.

    Model_1 reads the model.csv file generated by the previous trainer
    
    Bdn takes in the raw data downloaded from maximo and removes the unnecessary columns to speed up computation
    
    Test_dict takes in the dictionary of weights from model_1
    
    Spreader_details takes in the list of spreaders taken from Maximo
    
    Pm_details takes in the PMS WO history downloaded from Maximo

After running the model, save.csv is the state of the dataframe after tagging, before adding the days from PM to BDN.
    
    Spreader_list takes the list of spreader asset numbers from spreader_details
    
    Pm_history is a dictionary of PM dates for all the spreaders
    
    Days_list is a list is initialised to store the number of days since PM to BDN.

To add the column of days from PM to BDN, the loop goes through every row in the dataframe and checks if the assetnum is in the keys of the pm_history dictionary (i.e Check that the assetnum is correct and not some random string of numbers).
If it is, find the minimum positive value for the date of BDN minus date of PM and append it to the list. 
If None is found or the assetnum is not in the keys, then append None to the list.

At the end of the for loop, add days_list as a new column in the dataframe named "days since PM".

For the random numbers in the dataframe in “assetnum”, replace them with “asset not known” so that they can be consolidated
Output the dataframe as a csv named “all_bdn.csv” which is used by the dashboard to update its data.

## Primitive Files
### Primitives.py
This module contains the basic functions used to read a csv file.
To understand the different functions, open the file and read the comments

### Read_data.py
This module builds upon primitives.py to provide more advanced functions such as finding the last PM date for a given spreader, splitting a dataframe based on whether a specifed column is filled in or blank etc.
To understand all the different functions, open the file and read the comments.