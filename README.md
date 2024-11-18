# DatLeak
Methods for detection of data leakage in dataset.


When using BIDSscramble, a tool designed to anonymize BIDS datasets by randomizing the data, it's important to implement safeguards against potential data leakage. Data leakage can occur if scrambled identifiers inadvertently retain patterns that could be traced back to original participants. Hence DatLeak can be run to test for data leakage. 

This script detects data leakage by comparing an original dataset with a scrambled version. It calculates metrics like partial and full leakage percentages, average matching cells per row, and their standard deviation. The script accepts command-line inputs for the dataset files (CSV or TSV) and an optional ignore value, making it easy to use directly from the terminal.


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
