import React, {useState, useEffect} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs';
import Typography from '@mui/material/Typography';
import Connection from "./APIConnection";
import {CircularProgress} from "@mui/material";


export default function GetDatasetPython({dataset}) {
    const token = Connection.user?.token;
    const [columns, setColumns] = useState("")
    const [code, setCode] = useState(<CircularProgress/>)

    let domain = window.location.href.split('/')[2];
    domain = domain.split(':')[0]

    const host = `http://api.${domain}`

    useEffect(() => {
        Promise.all(dataset.columns.map(column =>
            Connection.fetch(column)
                .then(r => r.content)
                .then(col => `      '${col.name}': ${col.id},`)
        ))
            .then(cols => setColumns(cols.join('\n')))
    }, [dataset])

    useEffect(() => {
        if (!columns)
            setCode(<CircularProgress/>)
        else
            setCode(
                <SyntaxHighlighter language="python" style={docco}>{
                    `# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

import urllib3

host = "${host}"
headers = {'Authorization': 'Bearer ${token}'}

# Configuration
verbose = True
if verbose:
    import time

# Add additional dataset ids to download additional datasets
dataset_ids = [${dataset.id}]
dataset_metadata = {}  # Will have keys=dataset_id, values=Dict of dataset metadata
column_metadata = {}  # Will have keys=dataset_id, values=Dict of column metadata
datasets = {}  # Will have keys=dataset_id, values=pandas DataFrame of data

# Download data
start_time = time.time()
if verbose:
    print(f"Downloading {len(dataset_ids)} datasets from {host}")

for dataset_id in dataset_ids:
    dataset_start_time = time.time()
    if verbose:
        print(f"Downloading dataset {dataset_id}")
    r = urllib3.request('GET', f"{host}/datasets/{dataset_id}/", headers=headers)
    try:
        json = r.json()
    except:
        print(f"Non-JSON response while downloading {dataset_id}: {r.status}")
        continue
    if r.status != 200:
        print(f"Error downloading dataset {dataset_id}: {r.status}")
        continue
    columns = json.get('columns', [])
    json['columns'] = []

    dataset_metadata[dataset_id] = json

    if verbose:
        print(f"Dataset {dataset_id} has {len(columns)} columns to download")
    # Download the data from all columns in the dataset
    datasets[dataset_id] = pandas.DataFrame()
    for i, column in enumerate(columns):
        if verbose:
            print(f"Downloading dataset {dataset_id} column {i}")
        r = urllib3.request('GET', column, headers=headers)
        try:
            json = r.json()
        except:
            print(f"Non-JSON response while downloading from {column}: {r.status}")
            continue
        if r.status != 200:
            print(f"Error downloading column {dataset_id}: {r.status}")
            continue

        # Download the data from all rows in the column
        v = urllib3.request('GET', json.get('values'), headers=headers)
        if v.status != 200:
            print(f"Error downloading values for dataset {dataset_id} column {json.get('name')}: {v.status}")
            continue
        try:
            datasets[dataset_id][json.get('name')] = v.data.decode('utf-8').split('\\n')
        except:
            print(f"Cannot translate JSON response into DataFrame for column values {json.get['values']}")
            continue

        column_metadata[dataset_id] = json

    if verbose:
        print(f"Finished downloading dataset {dataset_id} in {time.time() - dataset_start_time} seconds")

if verbose:
    print(f"Finished downloading {len(dataset_ids)} datasets in {time.time() - start_time} seconds")

`
                }</SyntaxHighlighter>
            )
    }, [columns, dataset.id, host, token])

    return (
        <React.Fragment>
            <Typography>
                Python Code
            </Typography>

            {code}
        </React.Fragment>
    )
}
