import React, {useEffect, useState} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import {getToken} from "./Api"
import Typography from '@material-ui/core/Typography';


export default function GetDatasetPython({dataset}) {
  const [token, setToken] = useState('API_TOKEN');
  useEffect(() => {
  getToken().then(response => response.json()).then(data => {
      setToken(data.access_token)
    })
    
  }, [])
  
  let domain = window.location.href.split('/')[2];
  domain = domain.split(':')[0]

  const host = `http://${domain}:5001`
  const column_ids = dataset.columns.map(column => {
    return `      '${column.name}': ${column.id},`
  })
  const column_ids_str = column_ids.join('\n')
  const setupEnvString = `pip install batteryclient numpy`

  const codeString = `import batteryclient
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
${column_ids_str}
    }

    # download column data
    columns = {
      column_name: np.frombuffer(
        api_instance.get_column(dataset_id, column_id).read(), 
        dtype=np.float32
      ) for column_name, column_id in column_ids.items()
    }`

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


    <SyntaxHighlighter language="python" style={docco}>
      {codeString}
    </SyntaxHighlighter>
    </React.Fragment>
  )
}
