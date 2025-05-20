# DataLeak

## Table of Contents

- [Purpose](#purpose)
- [Methods](#methods)
  - [Pseudocode](#pseudocode)
  - [Usage](#usage)
  - [Output](#output)
  - [Full/Partial Leakage Calculation](#fullpartial-leakage-calculation)
- [HTML report](#html-report)
- [License](#license)

## Purpose
The purpose of this repository is to analyze information leakage in two neuro-imaging dataset of **Original** and **Scrambled/Synthetic**. We use 3 known methods to measure the similarity between slices by quantifying leakage across all dimensions of the image.

## Methods:
The idea of using three methods is to quantify information leakage is to complement each other’s strengths and limitations, providing a more robust and comprehensive assessment of potential leakage between the original and scrambled data.

`NOTE` Due to the computationally intensive nature of comparing large 3D to 4D arrays slice by slice, we implemented SSIM and Pearson correlation manually instead of using built-in functions from libraries like scipy. To optimize performance, we use [`numba`](https://pypi.org/project/numba/) to JIT-compile the function. However, numba does not support external Python callables like scipy.stats.pearsonr or skimage.ssim
- [`Pearson:`](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient) Pearson correlation coefficients
    - Useful for detecting global similarity patterns. However sensitive to scaling and outliers, but effective when relationships are purely linear.
- [`SSIM:`](https://en.wikipedia.org/wiki/Structural_similarity_index_measure) Structural similarity index measure
    - SSIM is designed to measure perceptual similarity, which takes into account luminance, contrast, and structure.
 
- [`np.allclose:`](https://numpy.org/doc/stable/reference/generated/numpy.allclose.html) Boolean matrix showing exact match (leakage) in centered data
    - A strict comparison to identify almost exact matches, indicating serious leakage. It also helps to detect accidental duplication or information leakage due to transformations.
### Pseudocode
### 3D
```terminal
# Given a dimension in [x, y, z]
For slice i = 0 to shape − 1: # for each original image slice
    For j = 0 to shape − 1:   # comparing all slices of scrambled 
    a. Extract 2D slices from data_o and data_s based on axis:
        If axis = 0,1,2: # representing [x, y, z]
            slice_o ← data_o[i, :, :] # extracting a plane/2D slice of original
            slice_s ← data_s[j, :, :] # extracting a plane/2D slice of scrambled
    b. Full leakage check:
        f_l_corrs[i, j] ← allclose(slice_o, slice_s)
    c. Compute Pearson correlation:
        p_corrs[i, j] ← p_corr(slice_o, slice_s)
    d. Compute SSIM:
        s_corrs[i, j] ← ssim(slice_o, slice_s)
return p_corrs, s_corrs, f_l_corrs
# returns a numpy array of shape (x,x), (y,y) or (z,z)
```
### 4D

```terminal
# Method 1
For time t = 0 to shape − 1: 
    a. compute 3D as above
return mean(3D)

# Method 2
```
## Usage
```terminal
python run.py <Original Base Dir> <Scrambled Base Dir> [report]
```
- Original/Scrambled base directory: The function searches for images, given one directory above all images
- Report is optional. Takes two arguments of True/False. By default is False
### Example
```terminal
python run.py "usecase2.2/input" "usecase2.2/scrambled" False"
```
## Output
```terminal
 - File shape: (x, y, z, [t])
 - Subject ID: ID
    - Partial Leakage[X]: leakage value
    - Partial Leakage[Y]: leakage value
    - Partial Leakage[Z]: leakage value
- Partial Leakage: %
- Full Leakage: %\begin{matrix}
```
## Full/Partial Leakage Calculation
### `Full Leakage:` 
We consider Full Leakage as identical. Meaning if an original image is 100% identical to the scrambled version. If Pearson Correlation returns a value of [0.999 - 1.0], backed up by SSIM/np.allclose return similar value in any slice across any dimension of [x, y, z].
### `Partial Leakage:` 
Partial Leakage is calculated by using a threshold range of [0.5 - 0.999] from the distribution of **max values** extracted from the Pearson correlation, SSIM, and np.allclose matrices.
- `x` refers to the dimensions of an image in the format dim[x, y, z], and `o,s` are `original` and `scrambled` respectively.
- The left matrix represents the **Pearson correlation** matrix with shape **(x, x)**, where `shape[0]` corresponds to the original dimensions, and `shape[1]` is the correlation between the original and scrambled images.
- The right matrix of shape **(x,)** shows the **maximum values** for each dimension, alongside their respective `x_original` and `x_scrambled` values.
From these matrices, Partial Leakage is computed based on the specified threshold.
```math
\left.
  \begin{matrix}
    x_{o1,s1} & \dots & x_{o1,sN} \\
    x_{o2,s1} & \dots & x_{o2,sN} \\
    \vdots    & \ddots & \vdots  \\
    x_{oN,s1} & \dots & x_{oN,sN} \\
  \end{matrix}
\right\}
\quad
\left.
  \begin{matrix}
    x_{\text{max}1} \\
    x_{\text{max}2} \\
    \vdots \\
    x_{\text{max}N}
  \end{matrix}
\right.
```

## HTML Report
To ensure transparency and verification, and allow for visual inspection of the results, an optional HTML report is generated alongside the leakage analysis. This report provides:

- A side-by-side visual snapshot of the original and scrambled data slices.
- A summary table displaying the computed values for:
    - Pearson correlation: min, max, mean along [x, y, z] dim
    - SSIM: min, max, mean along [x, y, z] dim
- Plots visualizing the distribution of correlation values, helping identify any unexpected alignment or leakage patterns.
    - Total distribution plot
    - Threshold distribution plot: Threshold is set between 0.5 - 0.999




This report is useful for both debugging and communicating the behavior of the leakage metric, especially in research or collaborative development settings.
## License
This project is licensed under the MIT License. So do as you wish :)
