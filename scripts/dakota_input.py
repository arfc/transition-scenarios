import jinja2


def load_template(in_template):
    """ Returns a jinja2 template from file.

    Parameters
    ---------
    in_template: str
        path and name of jinja2 template

    Returns
    -------
    output_template: jinja template object
    """
    with open(in_template, 'r') as default:
        output_template = jinja2.Template(default.read())
    return output_template


def render_input(xml_template, variable_dict, input_xml):
    """
    Formats the input file template's placeholder variables

    Parameters:
    -----------
    xml_template: str
        path to input file template
    variable_dict: dict of str
        contains the variables in the template file as keys, 
        and the value to apply as the value
    input_xml: str
        path to save the filled in template to 

    Returns:
    --------
    null
    """
    test_template = load_template(xml_template)
    config = test_template.render(variable_dict)
    with open(input_xml, 'w') as output:
        output.write(config)
    return
