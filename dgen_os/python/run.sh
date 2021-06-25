#!/bin/bash

# A Bash script that activates the conda environment and Docker container that
# allows users to run the Distributed Generation Market Demand (dGen) Model
# locally for testing purposes.

# --- TOOLS AND CODE ---

# This script is designed for users who have already downloaded the required
# tools (Docker, Anaconda, PgAdmin, and Git), forked a copy of the open-source
# dGen repository to their own GitHub account, and cloned the the forked
# repository to their local machine. If you have not already done so, please
# navigate to https://github.com/NREL/dgen, click the "Fork" button in the
# top right corner of the screen, and follow the instructions. Next, execute
# the following command:

# $ git clone https://github.com/<YOUR_GITHUB_USERNAME>/dgen.git

# --- CONFIGURING THE ENVIRONMENT ---

# This script assumes that you have already configured the required runtime
# environment by running the following commands:

# 1. Create the conda environment.

# $ conda env create -f dg3n.yml

# 2. Initialize a Docker container with PostgreSQL enabled.

# $ docker run --name postgis_1 -p 5432:5432 -e POSTGRES_USER=postgres -e
#   POSTGRES_PASSWORD=postgres -d mdillon/postgis

# 3. Connect to the PostgreSQL database in the Docker container.

# $ docker exec -it <CONTAINER_ID> psql -U postgres
# $ postgres=# CREATE DATABASE dgen_db;

# --- DATA ---

# This script also assumes you have already downloaded the data required for
# your run from OpenEI at https://data.openei.org/submissions/1931. Be sure to
# download the database and agent files that correspond to state or ISO region
# in which you are interested. After downloading the database and agent files,
# execute the following command to restore the database:

# $ cat /<PATH_TO_DATABASE>/dgen_db.sql | docker exec -i <CONTAINER_ID> psql -U
#   postgres -d dgen_db

# Once you have restored the database, you must open PgAdmin and create a new
# server. You may name it whatever you want, but enter "localhost" as the host
# name and "postgres" for both the username and password.

# --- TROUBLESHOOTING ---

# For more detailed instructions on how to configure the environment and
# download the necessary data, please see the README on the open-source dGen
# repository at https://github.com/NREL/dgen.

# --- CUSTOMIZE THE SCENARIO ---

# You can customize the scenario used to run the model by modifying the input
# sheet in the "excel" folder. Save a copy of the modified input sheet to the
# "input_scenarios" folder.

# --- ACTIVATING THE ENVIRONMENT ---

# Activate the conda environment.
conda activate dg3n

# Activate the Docker container.
docker start postgis_1

# --- RUN THE MODEL ---

# Navigate to where the model is located on your machine.
# $ cd <PATH_TO_MODEL>

# Run the model on a single agent for a single year.
python dgen_model.py

# --- SAVE THE RESULTS ---

# Results from the model run are placed in a SQL table named "agent_outputs"
# in a newly created schema located within the connected database.

# Note that the database will not persist if you terminate the Docker container,
# so to save the results locally, you must either download the "agent_outputs"
# table from the scheme containing the results or dump the entire database to a
# SQL file. To do the former, right click on the "agent_outputs" table in the
# PgAdmin tree view and select the export option you desire. To do the latter,
# execute the following command:

# $ docker exec <CONTAINER_ID> pg_dumpall -U postgres >
#   /../<PATH_TO_DATABASE>/dgen_db.sql

# The resulting SQL file can be restored according to the instructions above.
