
import pandas as pd

import csv
import os
import pathlib
import sys
import sqlite3 as lite

sys.path.append('../../../scripts/')


def udb_analysis(dat_file):
    # Import CURIE data from dat file into a dataframe
    # (deleted the heading of the dat file)
    names = [
        'assembly_id',
        'reactor_id',
        'reactor_type',
        'initial_uranium_kg',
        'initial_enrichment',
        'discharge_burnup',
        'discharge_date',
        'discharge_time',
        'total_assembly_decay_heat_kw',
        'name',
        'evaluation_date',
        'total_mass_g',
        'total_radioactivity_curies']
    df = pd.read_csv(dat_file,
                     sep='\s+',
                     index_col=False,
                     names=names)

    # Rearrange dataframe to only keep relevant columns
    date_isotope_mass = df[['discharge_date', 'name', 'total_mass_g']]
    date_mass = df[['discharge_date', 'total_mass_g']]

    # Rearrange dataframe to sum spent fuel mass by discharge date
    spent_fuel_mass = date_mass.groupby('discharge_date').sum()
    spent_fuel_mass_cum = spent_fuel_mass.cumsum()
    spent_fuel_mass_cum['total_mass_g'] = spent_fuel_mass_cum['total_mass_g'].apply(
        lambda x: x * 0.000001)
    spent_fuel_mass_cum = spent_fuel_mass_cum.rename(
        columns={'total_mass_g': 'total_mass_MTHM_CURIE'})
    spent_fuel_mass_cum.index.names = ['discharge_date']

    # Isotope list
    CURIE_isotope = date_isotope_mass.pivot_table(
        index='discharge_date', columns='name', aggfunc=sum)
    CURIE_isotope_cum_all = CURIE_isotope.cumsum()
    isotope_list = list(CURIE_isotope_cum_all)
    curie_isotope_list = [x[1] for x in isotope_list]

    return spent_fuel_mass_cum, CURIE_isotope_cum_all, curie_isotope_list


def udb_analysis_bu(dat_file):
    # Import CURIE data from dat file into a dataframe
    # (deleted the heading of the dat file)
    names = [
        'assembly_id',
        'reactor_id',
        'reactor_type',
        'initial_uranium_kg',
        'initial_enrichment',
        'discharge_burnup',
        'discharge_date',
        'discharge_time',
        'total_assembly_decay_heat_kw',
        'name',
        'evaluation_date',
        'total_mass_g',
        'total_radioactivity_curies']
    df = pd.read_csv(dat_file,
                     sep='\s+',
                     index_col=False,
                     names=names)

    # Rearrange dataframe to only keep relevant columns
    burnup_everything = df[['discharge_date', 'discharge_burnup']]

    # Rearrange dataframe to average spent fuel burn up by discharge date
    burn_up_grouped = burnup_everything.groupby('discharge_date').mean()

    return burn_up_grouped
