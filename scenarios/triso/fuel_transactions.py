from cymetric import timeseries


def used_fuel_transactions(transactions, fuels):
    """
    Adds up all the used fuel transactions for each fuel type in a new column.

    Parameters
    ----------
    transactions: pd.DataFrame
        All the material exchanges across the simulation.
    fuels: list of strs
        The types of fuel traded.
    """
    for fuel in fuels:
        transactions[f'used_{fuel}'] = \
            transactions.loc[
                transactions['Commodity'] == f'used_{fuel}']['Quantity']
        transactions[f'used_{fuel}'] = \
            transactions[f'used_{fuel}'].fillna(0)
        transactions[f'used_{fuel}_total'] = \
            transactions[f'used_{fuel}'].cumsum()

    return transactions


def fresh_fuel_transactions(transactions, fuels):
    """
    Adds up all the fresh fuel transactions for each fuel type in a new column.

    Parameters
    ----------
    transactions: pd.DataFrame
        All the material exchanges across the simulation.
    fuels: list of strs
        The types of fuel traded.
    """
    for fuel in fuels:
        transactions[f'fresh_{fuel}'] = transactions.loc[
            transactions['Commodity'] == f'fresh_{fuel}']['Quantity']
        transactions[f'fresh_{fuel}'] = \
            transactions[f'fresh_{fuel}'].fillna(0)
        transactions[f'fresh_{fuel}_total'] = \
            transactions[f'fresh_{fuel}'].cumsum()

    return transactions


def total_used_fr_fuel(transactions, fuels):
    """
    Adds the fresh fuel of each fuel type and total used fuel of each fuel
    type to a separate total for fresh and used fuel.

    Parameters
    ----------
    transactions: pd.DataFrame
        All the material exchanges across the simulation.
    fuels: list of strs
        The types of fuel traded.
    """
    transactions[f'total_fresh_fuel'] = 0
    transactions[f'total_used_fuel'] = 0

    for fuel in fuels:
        transactions.ffill(inplace=True)
        transactions[f'total_fresh_fuel'] += \
            transactions[f'fresh_{fuel}_total']
        transactions[f'total_used_fuel'] += \
            transactions[f'used_{fuel}_total']

    return transactions


def fuel_received(evaler, fuels, receivers):
    """
    Creates a DataFrame of the total fuel received by each receiver.
    The idea here is different than used_fuel_transactions(),
    fresh_fuel_transactions(), and total_used_fr_fuel() in that it is not
    looking at the transactions DataFrame, but rather the transactions for
    specific receivers.

    Parameters
    ----------
    evaler: cymetric.evaluator.Evaluator
        The object that takes in the sqlite database and can create DataFrames.
    fuels: list of strs
        The types of fuel traded.
    receivers: list of strs
        The archetypes that receive fuel.

    Returns
    -------
    received: pd.DataFrame
        The DataFrame of the total fuel received by each receiver.
    """

    for receiver in receivers:
        # set up the first fuel to create the DataFrame
        received_1 = timeseries.transactions(
            evaler=evaler, receivers=[f'{receiver}'], commodities=[fuels[0]])

        received = received_1.copy()
        received[f'{fuels[0]}_{receiver}'] = received['Mass']

        # set up the rest of the fuels if the list is longer than 1
        if len(fuels) > 1:
            for fuel in range(1, len(fuels)):
                received_next = timeseries.transactions(
                    evaler=evaler,
                    receivers=[f'{receiver}'],
                    commodities=[fuels[fuel]])

                received[f'{fuels[fuel]}_{receiver}'] = received_next['Mass']

        # create the total fuel received columns
        for fuel in fuels:
            received[f'{fuel}_{receiver}_total'] = \
                received[f'{fuel}_{receiver}'].cumsum()

    return received


def fuel_sent(evaler, fuels, senders):
    """
    Creates a DataFrame of the total fuel sent by each sender.
    The idea here is different than used_fuel_transactions(),
    fresh_fuel_transactions(), and total_used_fr_fuel() in that it is not
    looking at the transactions DataFrame, but rather the transactions for
    specific senders.

    Parameters
    ----------
    evaler: cymetric.evaluator.Evaluator
        The object that takes in the sqlite database and can create DataFrames.
    fuels: list of strs
        The types of fuel traded.
    senders: list of strs
        The archetypes that send fuel.

    Returns
    -------
    sent: pd.DataFrame
        The DataFrame of the total fuel sent by each sender.
    """

    for sender in senders:
        # set up the first fuel to create the DataFrame
        sent_1 = timeseries.transactions(
            evaler=evaler, senders=[f'{sender}'], commodities=[fuels[0]])

        sent = sent_1.copy()
        sent[f'{fuels[0]}_{sender}'] = sent['Mass']

        # set up the rest of the fuels if the list is longer than 1
        if len(fuels) > 1:
            for fuel in range(1, len(fuels)):
                sent_next = timeseries.transactions(
                    evaler=evaler,
                    senders=[f'{sender}'],
                    commodities=[fuels[fuel]])

                sent[f'{fuels[fuel]}_{sender}'] = sent_next['Mass']

        # create the total fuel sent columns
        for fuel in fuels:
            sent[f'{fuel}_{sender}_total'] = \
                sent[f'{fuel}_{sender}'].cumsum()

    return sent
