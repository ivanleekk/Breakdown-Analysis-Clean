# PSA-Breakdown-Analysis-Clean
Only contains the source code without any data

## Usage
### Model Training
In order to use this, download the following sets of data.
1) Breakdown records for the time frame to be analysed
2) Spreader PM Records for the relevant period
3) List of spreaders

If no model has been created/a new model has to be trained, go to the run_auto_learner.py file and change the string in line 7 to the name of your breakdown record.
Adjust the fraction of data to be used as training data if needed.

Once a model has been created, it is saved as model.csv

### Normal Use
To use the model to classify the data, use the run_with_output.py file and rename the bdn file to the name of your breakdown records file, spreader_details to your spreader details and pm_details to your PM details.

After running the script, the new code assigned to it is saved in the "new code" column and the number of days since PM will be stored in the "days since PM" column

Once done, open up the breakdown analysis Power BI dashboard and press refresh to view the new data.
