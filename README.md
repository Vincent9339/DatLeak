# DatLeak
Methods for detection of data leakage in a dataset.


When anonymizing data, for instance, by randomizing data orders, it's important to implement safeguards against potential data leakage. Data leakage can occur if scrambled variables inadvertently retain patterns that could be traced back to the original participants. Hence DatLeak can be run to test for data leakage. 

This script detects data leakage by comparing an original dataset with an anonymized version. It calculates percentages of full leakage (all variables are the same), and partial leakage (some variables are the same). In the latter case, it does so by averaging matching cells (per row). The script accepts command-line inputs for the dataset files (CSV or TSV) and an optional ignore value.


### Usage 

```
python DatLeak.py original_file scrambled_file [ignore_value]
```

### Example use

```
python DatLeak.py data_original.csv data_scramble.csv -999
```

### Ouput 

```
Partial Leakage: 99.78%
Full Leakage: 0.00%
Average Matching Cells per Row: 4.98
Standard Deviation of Matching Cells per Row: 1.68
```
