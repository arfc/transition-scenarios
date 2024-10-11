import os
import pandas as pd
import pytest
import tempfile
import xml.etree.ElementTree as ET
from existing_lwr import generate_facility_xml, extract_power_cap

def test_generate_facility_xml():
    """
    Test the generate_facility_xml function.
    """
    # Create a sample DataFrame
    data = {
        'Reactor name': ['Reactor1'],
        'Startup date (year) b': [2000],
        'Actual retirement (year)': [None],
        'Core size (number of assemblies)': [157]
    }
    df = pd.DataFrame(data)

    # Call the generate_facility_xml function
    reactor = 'Reactor1'
    xml_string = generate_facility_xml(df, reactor)

    # Expected XML string
    expected_xml = textwrap.dedent("""
        <facility>
        <name>Reactor1</name>
        <lifetime>960</lifetime>
        <config>
            <Reactor>
            <fuel_incommods>  <val>fresh_uox</val> </fuel_incommods>
            <fuel_inrecipes>  <val>fresh_uox</val> </fuel_inrecipes>
            <fuel_outcommods> <val>used_uox</val> </fuel_outcommods>
            <fuel_outrecipes> <val>used_uox</val> </fuel_outrecipes>
            <cycle_time>18</cycle_time>
            <refuel_time>1</refuel_time>
            <assem_size>427.38589211618256</assem_size>
            <n_assem_core>157</n_assem_core>
            <n_assem_batch>80</n_assem_batch>
            <power_cap></power_cap>
            <longitude></longitude>
            <latitude></latitude>
            </Reactor>
        </config>
        </facility>
    """).strip()

    # Verify the generated XML string
    assert xml_string == expected_xml

def test_extract_power_cap():
    """
    Test the extract_power_cap function.
    """
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample XML files
        xml_content = """
        <facility>
            <name>Reactor1</name>
            <config>
                <Reactor>
                    <power_cap>1000</power_cap>
                </Reactor>
            </config>
        </facility>
        """
        file_path = os.path.join(temp_dir, 'reactor1.xml')
        with open(file_path, 'w') as f:
            f.write(xml_content)

        xml_content = """
        <facility>
            <name>Reactor2</name>
            <config>
                <Reactor>
                    <power_cap>1500</power_cap>
                </Reactor>
            </config>
        </facility>
        """
        file_path = os.path.join(temp_dir, 'reactor2.xml')
        with open(file_path, 'w') as f:
            f.write(xml_content)

        # Call the extract_power_cap function
        power_cap_dict = extract_power_cap(temp_dir)

        # Expected power capacities
        expected_power_cap_dict = {
            'Reactor1': 1000,
            'Reactor2': 1500
        }

        # Verify the extracted power capacities
        assert power_cap_dict == expected_power_cap_dict
