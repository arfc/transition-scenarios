# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------

project = 'Transition Scenarios'
copyright = '2024, ARFC'
author = 'ARFC'

# The full version, including alpha/beta/rc tags
release = '0.01'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# myst_parser adds support for Markedly Structured Text, includes more features
# sphinx.ext.napoleon allows for a google/numpy docstring style
# sphinx.ext.duration represents time durations in a human-readable format
# sphinx.ext.autosectionlabel labels sections
# sphinx.ext.autodoc generates docs from docstrings
# sphinx.ext.autosummary generates summary tables of modules and packages
# sphinx.ext.intersphinx allows for linking to external documentation sites
# sphinx.ext.viewcode adds "View Source" links to docs
# sphinx.ext.mathjax renders mathematical expressions written in LaTeX
# sphinx.ext.coverage assesses and visualizing the test coverage
# nbsphinx includes Jupyter Notebooks in docs
# sphinxcontrib.mermaid create diagrams in markdown

extensions = ["myst_parser",
              "sphinx.ext.napoleon",
              "sphinx.ext.duration",
              "sphinx.ext.autosectionlabel",
              "sphinx.ext.autodoc",
              "sphinx.ext.autosummary",
              "sphinx.ext.intersphinx",
              "sphinx.ext.viewcode",
              "sphinx.ext.mathjax",
              "sphinx.ext.coverage",
              "nbsphinx",
              "sphinxcontrib.mermaid"]

# Suffixes that are useable
# source_suffix = {
#     '.rst': 'restructuredtext',
#     '.txt': 'markdown',
#     '.md': 'markdown',
# }

# make sure you have a unique autolabelled target
autosectionlabel_prefix_document = True
# Sphinx will create explicit targets for all your sections, the name of target
# has the form {path/to/page}:{title-of-section}.

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# List of modules to be mocked up.
autodoc_mock_imports = ['pyne', 'd3ploy', 'seaborn', 'xmltodict',
                        'dataframe_analysis', 'predicting_the_past_import',
                        'create_AR_DeployInst']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'astropy': ('https://docs.astropy.org/en/stable/', None),
    'cyclus': ('https://fuelcycle.org/', None)
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['source/_static']
