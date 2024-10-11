import pandas as pd
import textwrap


def generate_facility_xml(df, reactor):
    """
    Generate the XML string for a reactor facility from the given dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe containing the information about the reactor.
    reactor : str
        The name of reactor to generate the XML for.

    Returns
    -------
    str
        The XML string for the reactor facility.

    Notes
    -----
    * This function assumes that LWRs will all operate for 80 years unless they
      are prematurely retired.
    * The user must confirm the latitude, longitude, and power capacity of each
      reactor.
    """
    # Find the index of the reactor in the dataframe
    reactor_index = df[df['Reactor name'] == reactor].index[0]

    # Extract the information about the reactor
    reactor_name = df['Reactor name'].iloc[reactor_index]
    startup_date = df['Startup date (year) b'].iloc[reactor_index]
    retirement_date = df['Actual retirement (year)'].iloc[reactor_index]
    core_size = df['Core size (number of assemblies)'].iloc[reactor_index]

    # If retirement_date is NaN, set it to 80 years after the startup date
    if pd.isna(retirement_date):
        retirement_date = int(startup_date) + 80
    else:
        retirement_date = int(retirement_date)

    # Calculate the lifetime of the reactor in months
    life_months = str((retirement_date - int(startup_date)) * 12)

    # Format the information into the desired XML structure
    xml_string = textwrap.dedent(f"""
        <facility>
        <name>{reactor_name}</name>
        <lifetime>{life_months}</lifetime>
        <config>
            <Reactor>
            <fuel_incommods>  <val>fresh_uox</val> </fuel_incommods>
            <fuel_inrecipes>  <val>fresh_uox</val> </fuel_inrecipes>
            <fuel_outcommods> <val>used_uox</val> </fuel_outcommods>
            <fuel_outrecipes> <val>used_uox</val> </fuel_outrecipes>
            <cycle_time>18</cycle_time>
            <refuel_time>1</refuel_time>
            <assem_size>427.38589211618256</assem_size>
            <n_assem_core>{core_size}</n_assem_core>
            <n_assem_batch>80</n_assem_batch>
            <power_cap></power_cap>
            <longitude></longitude>
            <latitude></latitude>
            </Reactor>
        </config>
        </facility>
        """).strip()
    return xml_string


# This is the code I used to pull the power capacities from the xml files after
# I manually entered them. For your sake, I will just provide the dictionary
# and the code you can use to add it to the csv.
def extract_power_cap(directory):
    """
    Extract the power_cap values from the XML files in the given directory.

    Parameters
    ----------
    directory : str
        The directory containing the XML files.

    Returns
    -------
    dict
        A dictionary containing the power_cap values for each reactor.
    """

    # Initialize an empty dictionary to store the power_cap values
    power_cap_dict = {}

    # Iterate over each XML file in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            file_path = os.path.join(directory, filename)

            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract the reactor name and power_cap value
            reactor_name = root.find('name').text
            power_cap_element = root.find('.//power_cap').text

            # Add the power_cap value to the dictionary
            power_cap_dict[reactor_name] = int(power_cap_element)

    return power_cap_dict
