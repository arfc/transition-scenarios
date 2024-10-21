import os
from pathlib import Path
import textwrap
import pandas as pd


def create_output_directory(output_dir):
    """
    Create the output directory if it doesn't exist.

    Parameters
    ----------
    output_dir : str
        The directory to output the XML files to.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


def generate_xml_string(state, number, reactor_type, attributes):
    """
    Generate the XML string for a single reactor.

    Parameters
    ----------
    state : str
        The state where the reactor is located.
    number : int
        The reactor number.
    reactor_type : str
        The type of reactor ('large' or 'small').
    attributes : dict
        The dictionary containing the reactor attributes.

    Returns
    -------
    str
        The generated XML string.
    """
    return textwrap.dedent(f"""
    <facility>
        <name>{state}_{number}_{reactor_type}_est</name>
        <lifetime>{attributes['lifetime']}</lifetime>
        <config>
            <Reactor>
                <fuel_incommods>
                    <val>fresh_uox</val>
                </fuel_incommods>
                <fuel_inrecipes>
                    <val>fresh_uox</val>
                </fuel_inrecipes>
                <fuel_outcommods>
                    <val>used_uox</val>
                </fuel_outcommods>
                <fuel_outrecipes>
                    <val>used_uox</val>
                </fuel_outrecipes>
                <cycle_time>
                    {attributes['cycle_time']}
                </cycle_time>
                <refuel_time>
                    {attributes['refuel_time']}
                </refuel_time>
                <assem_size>
                    {attributes['assem_size']}
                </assem_size>
                <n_assem_core>
                    {attributes['n_assem_core']}
                </n_assem_core>
                <n_assem_batch>
                    {attributes['n_assem_batch']}
                </n_assem_batch>
                <power_cap>{attributes['power_cap']}</power_cap>
            </Reactor>
        </config>
    </facility>
    """).strip()


def write_xml_to_file(output_dir, state, number, reactor_type, xml_string):
    """
    Write the XML string to a file.

    Parameters
    ----------
    output_dir : str
        The directory to output the XML files to.
    state : str
        The state where the reactor is located.
    number : int
        The reactor number.
    reactor_type : str
        The type of reactor ('large' or 'small').
    xml_string : str
        The generated XML string.

    Returns
    -------
    None
    """
    file_path = os.path.join(
                              output_dir,
                              f"{state}_{number}_{reactor_type}_est.xml")
    with open(file_path, 'w') as f:
        f.write(xml_string)


def generate_est_facility_xml(df, output_dir, reactor_types):
    """
    Generate the XML string for the estimated facilities from
    the given dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the information about the reactors.
    output_dir : str
        The directory to output the XML files to.
    reactor_types : dict
        The dictionary containing the reactor types and their attributes.

    Returns
    -------
    None
    """
    create_output_directory(output_dir)

    for state in range(1, len(df['Plant state'])):
        st = df.loc[state, 'Plant state']
        num_large = df.loc[state, 'Number_sites_space_large']
        num_small = df.loc[state, 'Number_sites_space_small']

        # Write the XML files for each large reactor in this state
        for number in range(int(num_large)):
            xml_string = generate_xml_string(
                                              st, number, 'large',
                                              reactor_types['large'])
            write_xml_to_file(output_dir, st, number, 'large', xml_string)

        # Write the XML files for each small reactor in this state
        for number in range(int(num_small)):
            xml_string = generate_xml_string(
                                              st, number, 'small',
                                              reactor_types['small'])
            write_xml_to_file(output_dir, st, number, 'small', xml_string)

    print('Successfully generated reactor XML files.')


# Example usage
if __name__ == "__main__":
    import camelot

    report_url = '''https://fuelcycleoptions.inl.gov/SiteAssets/SitePages/Home/
    Evaluation%20of%20NPP%20and%20CPP%20Sites%20Aug%2016%202024.pdf'''

    # Define the data
    tables = camelot.read_pdf(report_url, pages='17')
    data = tables[0].df

    # Extract header and data
    header = data.loc[0]
    data = data[1:]

    # Rename the columns
    data.columns = header

    current_operating = data[[data.columns[0]]]
    current_operating['Number_sites_space_large'] = data[[data.columns[-2]]]
    current_operating['Number_sites_space_small'] = data[[data.columns[-1]]]

    reactor_types = {
        'large': {
            'power_cap': 1117,
            'column': 'Number_sites_space_large',
            'lifetime': 960,
            'cycle_time': 18,
            'refuel_time': 1,
            'assem_size': 427.38589211618256,
            'n_assem_core': 193,
            'n_assem_batch': 80
        },
        'small': {
            'power_cap': 600,
            'column': 'Number_sites_space_small',
            'lifetime': 720,
            'cycle_time': 18,
            'refuel_time': 1,
            'assem_size': 71.2309820194,
            'n_assem_core': 111,
            'n_assem_batch': 46
        }
    }

    curr_dir = Path(os.path.dirnam(__file__))
    output_dir = str((curr_dir / "../reactors/lwrs_est").resolve())
    generate_est_facility_xml(current_operating, output_dir, reactor_types)
