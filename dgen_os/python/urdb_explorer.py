
"""
based on combination of dGen Tariff class and Vapor's datafetcher
"""
from python import config
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import numpy as np
# import pandas as pd
import codecs
import json
import csv
import logging
import os

import datetime as dt

import concurrent.futures as cf
import itertools
import io


logging.getLogger("requests").setLevel(logging.WARNING)

class FetchTariffs():
    """
    Download U.S. tariffs from OpenEI API
    https://openei.org/services/doc/rest/util_rates/?version=3
    Inputs
    ------
    TBD
    
    Methods
    -------
    TBD
    """

    def __init__(self, limit = 50, 
                urdb_api_key=config.OPEN_EI_API_KEY,
                urdb_api_email=config.OPEN_EI_API_EMAIL,
                workers=config.THREAD_WORKERS):

        self.urdb_api_key = urdb_api_key
        self.urdb_api_email = urdb_api_email

        self.limit = limit

        self.workers = workers

    def _requests_retry_session(self, retries=10,
                            backoff_factor=1,
                            status_forcelist=(429, 500, 502, 504),
                            session=None):
        """https://www.peterbe.com/plog/best-practice-with-retries-with-requests"""
        session = session or requests.Session()
        session.verify = False
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def _tariff_worker(self, job):

        # --- unpack job ---
        lon, lat, sector = job

        # --- initialize sesson ---
        retry_session = self._requests_retry_session()

        logging.info(f"Downloading tariff file for {lon}_{lat}...")
        
        input_params = {'version':'latest',
            'format':'json',
            'detail':'full',
            'limit': self.limit,
            'api_key': self.urdb_api_key,
            'lon': lon,
            'lat': lat,
            'sector': sector,
            'approved':'true'}

        # --- Find url for closest point ---
        lookup_base_url = ' https://api.openei.org/utility_rates?'
        lookup_query_url = "version={version}&format={format}&limit={limit}&api_key={api_key}&lat={lat}&lon={lon}&sector={sector}&approved={approved}".format(**input_params)

        lookup_url = lookup_base_url + lookup_query_url
        
        lookup_response = retry_session.get(lookup_url)

        if lookup_response.ok:
            
            lookup_json = lookup_response.json()
            links = {x['label']: None for x in lookup_json['items']}

            # kind of stupid but do not want threads spawning threads as it could get out of hand
            # https://stackoverflow.com/a/51116667

            for uri in links.keys():

                lookup_query_url = f"version={3}&format=json&api_key={self.urdb_api_key}&detail=full&getpage={uri}"
                lookup_url = lookup_base_url + lookup_query_url
                retry_session = self._requests_retry_session()

                lookup_response = retry_session.get(lookup_url)
                content = lookup_response.content
                tariff_original = json.loads(content, strict=False)['items'][0]

                if 'enddate' not in tariff_original.keys():

                    tariff_original = {'lon': lon, 'lat': lat, 'sector': sector, **tariff_original}
                    
                    filepath = os.path.join('data', 'urdb_tariffs', f"{int(lon*1E3)}_{int(lat*1E3)}_{sector.lower()}_{uri}.json")

                    with open(filepath, "w") as outfile:
                        json.dump(tariff_original, fp = outfile, indent=0)

                    links[uri] = filepath
                
                else:
                    logging.info(f'end date found for uri: {uri}')
            
            return links

    def fetch(self, points):
        """
        Creates dict with {job:path_to_tariff_json}.
        Input
        -----
        points(iterable): iterable of lon/lat/sector tuples
        """
        logging.info(f'Beginning tariff download using {self.workers} thread workers')

        # --- Initialize Session w/ retries ---
        if self.workers > 1:

            with cf.ThreadPoolExecutor(max_workers=self.workers) as executor:
                futures = [executor.submit(self._tariff_worker, job)
                           for job in points]
                results = [f.result() for f in futures]

        else:
            results = []
            for job in points:
                results.append(self._tariff_worker(job))

        self.resource_file_paths = results
        self.resource_file_paths_dict = dict(zip(points, results))

        logging.info('....finished data download')
