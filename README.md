# Hollowfoot


[![PyPI badge](https://img.shields.io/pypi/v/hollowfoot.svg)](https://pypi.python.org/pypi/hollowfoot)



A work-flow engine for performing analysis of experimental X-ray data
using xraylarch and other domain-specific frameworks.

A hollowfoot analysis is:

**Declarative:** A typical analysis workflow in hollowfoot is best
 thought of as a series of steps to be performed on some underlying
 data. The analysis engine is responsible for executing the steps for
 you when needed.

**Jupyter-first:** Many analysis frameworks, like *xraylarch*,
  provide tools that are used as part of some larger analysis
  application. *Hollowfoot* aims to extend these tools so that they
  can be used as first-class objects in a jupyter notebook
  environment.


## Documentation

Sphinx-generated documentation for this project can be found here:
https://spc-group.github.io/hollowfoot/


## Usage

An example workflow for XAFS analysis might look like:

```python
import hollowfoot as hf

analysis = (
    XAFSAnalysis  # What kind of analysis are we doing?
        .from_aps_20bmb("my_data_folder/")  # Load data from disk
        .to_mu("mono-energy", "It", "I0", is_transmission=True)  # Apply reference correction
        .plot_mu()  # Plot all data sets together
        .merge()  # Merge data sets into a single group
        .fit_edge_jump()  # Do some normalization, etc
        .subtract_background()  # Convert from µ(E) to χ(E)
        .plot_mu()  # Plot the single, corrected dataset
    	.summarize()  # Print out a summary of the steps that have been taken
)
```

Notice how each line of the previous code snippet describes a concise
step of analysis. These steps can be re-ordered or commented out,
making for easy comparisons between analysis strategies.


## Installation

The following will download the package and load it into the python environment.

```bash
$ pip install hollowfoot
```

## Running the Tests
-----------------

```bash
$ uv run --dev pytest
```
