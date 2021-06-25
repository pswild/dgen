#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu May 24 17:24:00 2021

@author: pwild
"""

# --- Imports ---

# External Packages
import pandas as pd
import psycopg2 as pg

# ------------------------------------------------------------------------------


def connect_to_db(database):
    """
    Connects to local PostgreSQL database.
    Returns connection.
    """

    # Connect to database.
    con = pg.connect(
        host='localhost',
        port=5432,
        database=database,
        user='postgres',
        password='postgres'
    )

    return(con)


def disconnect_from_db(con):
    """Disconnects from local PostgreSQL database."""

    # Close connection.
    con.close()

    return


def query_db(sql, con):
    """
    Queries local PostgreSQL database.
    Returns dataframe containing results of query.
    """

    # Results of query.
    results = None

    try:

        # Read results of SQL query into dataframe.
        results = pd.read_sql(sql, con)

        return(results)

    except Exception as e:

        print('Error: ', e)

        exit(1)


def compare_results(con):
    """
    Compares results of base case and test case.
    Returns True and null dataframe if all elements are equal.
    Returns False and dataframe with elements that differ otherwise.
    """

    # Read base results into dataframe.
    base_sql = """
    SELECT *
    FROM diffusion_results_single_agent_base_case.agent_outputs
    """
    base_results = query_db(sql=base_sql, con=con)

    print('Base results: ', base_results)

    # Read test results into dataframe.
    test_sql = """
    SELECT *
    FROM diffusion_results_single_agent_test_case.agent_outputs
    """
    test_results = query_db(sql=test_sql, con=con)

    print('Test results: ', test_results)

    # Check whether elements of base results and test results are the same.
    same = base_results.equals(test_results)

    # Elements that differ.
    diff = None

    if not equal:

        # Find which elements differ.
        diff = base_results.compare(test_results)

    return(same, diff)


# ------------------------------------------------------------------------------


if __name__ == '__main__':

    # Database name.
    database = 'dgen_db_de'

    # NOTE: schema names must be manually changed within SQL query.
    base_schema = 'diffusion_results_single_agent_base_case'
    test_schema = 'diffusion_results_single_agent_test_case'

    # NOTE: table name must be manually changed within SQL query.
    table = 'agent_outputs'

    # Connect to database.
    con = connect_to_db(database)

    # Compare results.
    same, diff = compare_results(con)

    if same:
        print("Congratulations, results match!")
    else:
        print("Sorry, results don't match... here's what's different:\n", diff)

    # Disconnect from database.
    disconnect_from_db(con)
