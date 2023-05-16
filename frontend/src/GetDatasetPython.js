import React, {useState, useEffect} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs';
import Typography from '@mui/material/Typography';
import Connection from "./APIConnection";
import {CircularProgress} from "@mui/material";


export default function GetDatasetPython({dataset}) {
  const [token, setToken] = useState(Connection.user?.token || 'API_TOKEN');
  const [columns, setColumns] = useState("")
  const [code, setCode] = useState(<CircularProgress/>)

  let domain = window.location.href.split('/')[2];
  domain = domain.split(':')[0]

  const host = `http://api.${domain}`
  const setupEnvString = `pip install batteryclient numpy`

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
# of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import batteryclient
from batteryclient.api import users_api
import numpy as np


token = '${token}'

configuration = batteryclient.Configuration(
    host="${host}/api",
    access_token=token
)

# Enter a context with an instance of the API client
with batteryclient.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = users_api.UsersApi(api_client)

    # get metadata on dataset
    dataset_id = ${dataset.id}
    api_response = api_instance.get_dataset(dataset_id)
    print(api_response)

    # get the data columns (delete those you don't need)
    column_ids = {
${columns}
    }

    # download column data
    columns = {
      column_name: np.frombuffer(
        api_instance.get_column(dataset_id, column_id).read(), 
        dtype=np.float32
      ) for column_name, column_id in column_ids.items()
    }`
          }</SyntaxHighlighter>
      )
  }, [columns])

  return (
      <React.Fragment>
        <Typography>
          Setup Dependencies
        </Typography>

        <SyntaxHighlighter language="bash" style={docco}>
          {setupEnvString}
        </SyntaxHighlighter>

        <Typography>
          Python Code
        </Typography>

        {code}
      </React.Fragment>
  )
}
