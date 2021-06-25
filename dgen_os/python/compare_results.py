#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Thu May 24 17:24:00 2021

@author: pwild
"""

# --- Imports ---

# Standard Library
import os
import sys
import logging

# External Packages
import pandas as pd
import psycopg2 as pg

# Local Modules
# ...

# --- Logging ---

log = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)s]: %(message)s',
    datefmt='%m/%d/%Y at %I:%M:%S %p',
    filename='../logs/compare_results.log',
    filemode='a',
    level=logging.INFO
)

# ------------------------------------------------------------------------------


class CompareResults():
    """
    Modular class for comparing the results of two dGen runs.
    - database: name of dGen database being hosted locally
    - base_schema: name of schema in which base results are stored
    - test_schema: name of schema in which test results are stored
    - table: name of table to compare between schemas
    """

    def __init__(
        self,
        database='dgen_db_de',
        base_schema='diffusion_results_single_agent_base_case',
        test_schema='diffusion_results_single_agent_test_case',
        table='agent_outputs'
    ):

        # Attributes.
        self.database = database
        self.base_schema = base_schema
        self.test_schema = test_schema
        self.table = table
        self.con = None

    def _connect_to_db(self):
        """Connects to local PostgreSQL database. Returns connection."""

        # Connect to database.
        self.con = pg.connect(
            host='localhost',
            port=5432,
            database=self.database,
            user='postgres',
            password='postgres'
        )

        return

    def _disconnect_from_db(self):
        """Disconnects from local PostgreSQL database."""

        # Close connection.
        self.con.close()

        return

    def _query_db(self, sql):
        """
        Queries local PostgreSQL database.
        - query: SQL query to be executed
        Returns dataframe containing results of query.
        """

        # Create variable for results.
        results = None

        try:

            # Read results of SQL query into dataframe.
            results = pd.read_sql(sql, self.con)

            return(results)

        except Exception as e:

            # Log error.
            log.error(e)

        return(results)

    def compare_results(self):
        """Compares results of base case and test case.
        Shows differences, if they exist."""

        # Connect to database.
        self._connect_to_db()

        # SQL query.
        sql = "SELECT * FROM diffusion_results_single_agent_base_case.agent_outputs"

        # Read base results into dataframe.
        base_results = self._query_db(sql=sql)

        # Read test results into dataframe.
        test_results = self._query_db(sql=sql)

        # Check whether base results are equal to test results.
        equal = base_results.equals(test_results)

        if equal:

            # Notify user.
            print("Congratulations, results match!")

        else:

            # Notify user.
            print("Sorry, results don't match...")

            # Find how base results differ from test results.
            differences = base_results.compare(test_results)

            # Show differences.
            print(differences)

        # Disconnect from database.
        self._disconnect_from_db()

        return(equal)

# ------------------------------------------------------------------------------


if __name__ == '__main__':

    # Database name.
    database = 'dgen_db_de'

    # Schema name(s).
    base_schema = 'diffusion_results_single_agent_base_case'
    test_schema = 'diffusion_results_single_agent_test_case'

    # Table name.
    table = 'agent_outputs'

    # Create new CompareResults object.
    compareResults = CompareResults(
        database=database,
        base_schema=base_schema,
        test_schema=test_schema,
        table=table
    )

    # Compare results.
    compareResults.compare_results()
