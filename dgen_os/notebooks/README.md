# Visualizing Results

Once you've run dGen and saved the results locally in a SQL database, you can
start analyzing the model's output.

1. Activate the appropriate conda environment.

`$ conda activate dg3n`

2. Activate the Docker container with PostgreSQL intialized. This can be
accomplished via the Docker Desktop app or the command line.

`$ docker start postgis_1`

3. Navigate to the directory containing your testing notebook.

`$ cd /path_to_dir/`

4. Launch Jupyter Notebook.

`$ jupyter notebook`

5. Run your testing notebook.
