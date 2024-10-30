from cyclus import nucname
from cymetric.tools import reduce, merge
import pandas as pd

# These functions are almost directly copied from cymetric, but they use the
# version of PyNE built in cyclus to do the isotopics instead of the package
# PyNE.


def transactions_nuc_built_in(
        evaler,
        senders=(),
        receivers=(),
        commodities=(),
        nucs=()):
    """
    Filter the Transaction Data Frame, which include nuclide composition, on
    specific sending facility and receving facility. Applying nuclides
    selection when required.

    Parameters
    ----------
    evaler : evaler
    senders :  of the sending facility
    receivers :  of the receiving facility
    commodities :  of the commodity exchanged
    nucs :  of nuclide to select.
    """

    compo = evaler.eval('Materials')

    df = transactions_built_in(evaler, senders, receivers, commodities)

    if len(nucs) != 0:
        nucs = format_nucs_built_in(nucs)
        compo = reduce(compo, [['NucId', nucs]])

    base_col = ['SimId', 'ResourceId']
    added_col = base_col + ['NucId', 'Mass']
    df = merge(df, base_col, compo, added_col)

    return df


def transactions_built_in(evaler, senders=(), receivers=(), commodities=()):
    """
    Filter the Transaction Data Frame on specific sending facility and
    receving facility.

    Parameters
    ----------
    evaler : evaler
    senders :  of the sending facility
    receivers :  of the receiving facility
    commodities :  of the commodity exchanged
    """

    # Initiate evaluation.
    trans = evaler.eval('Transactions')
    agents = evaler.eval('AgentEntry')

    rec_agent = agents.rename(index=str, columns={'AgentId': 'ReceiverId'})
    if len(receivers) != 0:
        rec_agent = rec_agent[rec_agent['Prototype'].isin(receivers)]

    send_agent = agents.rename(index=str, columns={'AgentId': 'SenderId'})
    if len(senders) != 0:
        send_agent = send_agent[send_agent['Prototype'].isin(senders)]

    # Clean Transaction PDF.
    rdc_table = []
    rdc_table.append(['ReceiverId', rec_agent['ReceiverId'].tolist()])
    rdc_table.append(['SenderId', send_agent['SenderId'].tolist()])
    if len(commodities) != 0:
        rdc_table.append(['Commodity', commodities])

    trans = reduce(trans, rdc_table)

    # Merge Sender to Transaction PDF.
    base_col = ['SimId', 'SenderId']
    added_col = base_col + ['Prototype']
    trans = merge(trans, base_col, send_agent, added_col)
    trans = trans.rename(index=str, columns={
                         'Prototype': 'SenderPrototype'})

    # Merge Receiver to Transaction PDF.
    base_col = ['SimId', 'ReceiverId']
    added_col = base_col + ['Prototype']
    trans = merge(trans, base_col, rec_agent, added_col)
    trans = trans.rename(index=str, columns={
                         'Prototype': 'ReceiverPrototype'})

    return trans


def format_nucs_built_in(nucs):
    """
    format the nuclide  provided by the users into a standard format:
    ZZAASSSS.

    Parameters
    ----------
    nucs: float
      of nuclides
    """
    return [nucname.id(nuc) for nuc in nucs]


def isotope_database(evaler, receivers, isotopes, commodities):
    """
    This function makes a DataFrame of transaction information
    for each isotope given in each of the given commodities.

    Parameters
    ----------
    evaler: cymetric.evaluator.Evaluator
        The object that takes in the sqlite database and can create DataFrames.
    receivers: list of strs
        The archetypes that receive the fuel.
    isotopes: list of strs
        The isotopes that are in the fuel.
    commodities: list of strs
        The commodities that are traded.

    Returns
    -------
    isotope_df: pd.DataFrame
        The database of the transactions for each isotope in each commodity at
        each time step.
    """

    isotope_db = transactions_nuc_built_in(
        evaler=evaler,
        receivers=receivers,
        commodities=commodities,
        nucs=isotopes)

    # Create the dataframe and populate the columns for each
    # isotope with zeros.
    isotope_df = evaler.eval('TimeList')
    for nucid in isotopes:
        isotope_df[nucid] = 0
        isotope_df[f'{nucid}_total'] = 0

    # Track the mass of each isotope stored at each time.
    for transaction in range(len(isotope_db)):
        for nucid in isotopes:
            if isotope_db.loc[transaction, 'NucId'] == int(nucid):
                mass = isotope_db.loc[transaction, 'Mass']
                time_step = isotope_db.loc[transaction, 'Time']
                isotope_df.loc[str(time_step), str(nucid)] = mass

    # Add up the totals for each isotope over time.
    for nucid in isotopes:
        isotope_df[f'{nucid}_total'] = isotope_df[nucid].cumsum()

    return isotope_df