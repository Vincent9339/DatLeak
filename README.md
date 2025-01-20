# DatLeak
Methods for detection of data leakage in a dataset.


When anonymizing data, for instance, by randomizing data orders, it's important to implement safeguards against potential data leakage. Data leakage can occur if scrambled variables inadvertently retain patterns that could be traced back to the original participants. Hence DatLeak can be run to test for data leakage. 

### Full Leakage

A row $i$ is considered to have **full leakage** if the number of matching cells equals the number of valid cells in that row. The condition for full leakage for row $i$ is:


```math
\text{Full Leakage for Row } i = 
\begin{cases}
1, & \text{if } \text{match\_count}_{i} = \text{valid\_mask\_sum}_{i} \\
0, & \text{otherwise}
\end{cases}
```
```math
\text{Full Leakage Percentage} = \left( \frac{\text{Full Leakage Count}}{\text{total\_rows}} \right) \times 100
```

### Partial Leakage

A row $i$ is considered to have **partial leakage** if the number of matching cells is greater than 0 but less than the number of valid cells in that row. The condition for partial leakage for row `i` is:

```math
\text{Partial Leakage for Row } i = 
\begin{cases}
1, & \text{if } 0 < \text{match\_count}_{i} < \text{valid\_mask\_sum}_{i} \\
0, & \text{otherwise}
\end{cases}
```
```math
\text{Partial Leakage Percentage} = \left( \frac{\text{Partial Leakage Count}}{\text{total\_rows}} \right) \times 100
```

This formula checks if some, but not all, valid cells match between the original and scrambled rows, indicating partial leakage. 

This script detects data leakage by comparing an original dataset with an anonymized version. It calculates percentages of full leakage (all variables are the same), and partial leakage (some variables are the same). In the latter case, it does so by averaging matching cells (per row). The script accepts command-line inputs for the dataset files (CSV or TSV) and an optional ignore value.

### Requirements
- pandas
- numpy
- python 3.x

### Usage 

```
python DatLeak.py original_file scrambled_file [ignore_value]
```
- <original_file>: Path to the CSV or TSV file containing the original data.
- <scrambled_file>: Path to the CSV or TSV file containing the scrambled data.
- [ignore_value]: A value to ignore during the comparison (e.g., NaN or any placeholder value).

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
- Partial Leakage: The percentage of rows with partial leakage.
- Full Leakage: The percentage of rows with full leakage.
- Average Matching cells per row.
- Standard Deviation of matching cells per row.
