# PSA-Breakdown-Analysis-Clean-
Only contains the source code without any data


In order to use this, download the following sets of data.
1) Breakdown records for the time frame to be analysed
2) Spreader PM Records for the relevant period
3) List of spreaders

If no model has been created/a new model has to be trained, go to the run_auto_learner.py file and change the string in line 11 to the name of your breakdown record.
Adjust the fraction of data to be used as training data if needed.

Once a model has been created, it is saved as results.csv

To use the model to classify the data, use the run_with_output.py file and rename the data file to the name of your breakdown records file.
The new code assigned to it is saved in the newcode column.

Once done, open up the breakdown analysis Power BI dashboard and press refresh to view the new data.
