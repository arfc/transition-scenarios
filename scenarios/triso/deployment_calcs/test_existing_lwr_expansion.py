import os
import shutil
import pytest
import pandas as pd
from existing_lwr_expansion import create_output_directory, \
                                   generate_xml_string, \
                                   write_xml_to_file, \
                                   generate_est_facility_xml


@pytest.fixture
def setup_test_dir():
    """
    Set up the test directory for the tests.
    """
    test_dir = 'test_output'
    os.makedirs(test_dir, exist_ok=True)
    yield test_dir


def test_create_output_directory(setup_test_dir):
    """
    Test the function that creates the output directory.
    """
    test_dir = setup_test_dir
    # Remove the directory if it exists to test creation
    shutil.rmtree(test_dir)
    create_output_directory(test_dir)
    assert os.path.exists(test_dir)


def test_generate_xml_string():
    """
    Test the function that generates the XML string for a reactor.
    """
    state = 'AL'
    number = 0
    reactor_type = 'large'
    attributes = {
        'lifetime': 960,
        'cycle_time': 18,
        'refuel_time': 1,
        'assem_size': 427.38589211618256,
        'n_assem_core': 193,
        'n_assem_batch': 80,
        'power_cap': 1117
    }
    xml_string = generate_xml_string(state, number, reactor_type, attributes)
    assert '<name>AL_0_large_est</name>' in xml_string
    assert '<power_cap>1117</power_cap>' in xml_string


def test_write_xml_to_file(setup_test_dir):
    """
    Test the function that writes the XML string to a file.
    """
    test_dir = setup_test_dir
    state = 'AL'
    number = 0
    reactor_type = 'large'
    xml_string = '<facility><name>AL_0_large_est</name></facility>'
    write_xml_to_file(test_dir, state, number, reactor_type, xml_string)
    file_path = os.path.join(test_dir, 'AL_0_large_est.xml')
    assert os.path.exists(file_path)
    with open(file_path, 'r') as f:
        content = f.read()
        assert '<name>AL_0_large_est</name>' in content


def test_generate_est_facility_xml(setup_test_dir):
    """
    Test the function that generates the XML files for the reactors.
    """
    test_dir = setup_test_dir
    data = {
        'Plant state': ['AL', 'AR'],
        'Number_sites_space_large': [1, 0],
        'Number_sites_space_small': [0, 1]
    }
    df = pd.DataFrame(data)
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
    generate_est_facility_xml(df, test_dir, reactor_types)
    large_file_path = test_dir
    small_file_path = test_dir

    # test that both exist
    assert os.path.exists(large_file_path)
    assert os.path.exists(small_file_path)

    # test that the files contain the correct name content
    with open(large_file_path + '/AL_0_large_est.xml', 'r') as f:
        content = f.read()
        assert '<name>AL_0_large_est</name>' in content
    with open(small_file_path + '/AR_0_small_est.xml', 'r') as f:
        content = f.read()
        assert '<name>AR_0_small_est</name>' in content

    # remove the test directory
    shutil.rmtree(test_dir)
