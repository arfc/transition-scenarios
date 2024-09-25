<!-- Transition Scenarios documentation master file, created by
   sphinx-quickstart on Mon Feb 19 13:18:08 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive. -->

# Welcome to Transition Scenarios's documentation!

```{toctree}
:maxdepth: 2

scripts_outline
analysis_doc
create_ar_deployinst_doc
create_cyclus_input_doc
dakota_input_doc
dataframe_analysis_doc
reactor_deployment_doc
merge_coordinates_doc
output_metrics_doc
predicting_the_past_import_doc
random_lifetime_extension_doc
transition_metrics_doc
transition_plots_doc
test_analysis_doc
test_create_AR_DeployInst_doc
test_dataframe_analysis_doc
test_output_metrics_doc
test_reactor_deployment_doc
test_transition_metrics_doc
```

# Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`


# Building the Docs
To compile the documentation, make sure you have all the requirements
installed, then run `make html` from the top level of the repository.

```{warning}
The docs are still in their nascent stage. If you find a
problem, please open an issue on
[github](https://github.com/arfc/transition-scenarios/issues).
```

## Docs Requirements
* sphinx
* myst_parser
* sphinx.ext.napoleon
* sphinx.ext.duration
* sphinx.ext.autosectionlabel
* sphinx.ext.autodoc
* sphinx.ext.autosummary
* sphinx.ext.intersphinx
* sphinx.ext.viewcode
* sphinx.ext.mathjax
* sphinx.ext.coverage
* nbsphinx
* sphinxcontrib.mermaid