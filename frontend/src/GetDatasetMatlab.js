import React, {useEffect, useState} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import {getToken} from "./Api"
import Typography from '@mui/material/Typography';


export default function GetDatasetMatlab({dataset}) {
  const [token, setToken] = useState('API_TOKEN');
  useEffect(() => {
  getToken().then(response => response.json()).then(data => {
      setToken(data.access_token)
    })
    
  }, [])
  
  let domain = window.location.href.split('/')[2];
  domain = domain.split(':')[0]

  const host = `http://${domain}:5001`
  const codeString = `%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 
% galvanalyser REST API access
%   - Matt Jaquiery (Oxford RSE) <matt.jaquiery@dtc.ox.ac.uk>
%
% 2022-11-21
%
% Download datasets from the REST API.
% Downloads all data for all columns for the dataset and reads them
% into a struct object. Data are under data{x}.columns.data.
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% login to galvanalyser > Generate API Token
token = '${token}';
apiURL = '${host}/Dataset';
options = weboptions('HeaderFields', {'Authorization' ['Bearer ' token]});

% Datasets can be referenced by name or by id. 
% Only the id is guaranteed to be unique.
% You can add in additional dataset_names or dataset_ids to also
% fetch the contents of those datasets.
dataset_names = [];
dataset_ids = [${dataset.id}]; % add additional dataset ids here if required

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% look up dataset ids if names provided
if exist('dataset_names', 'var') && ~ isempty(dataset_names)
    dataset_meta = webread(apiURL, options);
    dataset_ids = [dataset_ids dataset_meta(ismember({dataset_meta.name}, dataset_names)).id];
end

dataset_ids = string(dataset_ids(:));
dataset_ids = unique(dataset_ids);

data = {};

for i = 1:length(dataset_ids)
    d = dataset_ids(i);
    
    % get data
    dsURL = strcat(apiURL, '/', d);
    meta = webread(dsURL, options);
    
    % append column data in columns
    for c = 1:length(meta.columns)
        cURL = strjoin([dsURL, meta.columns(c).id], '/');
        stream = webread(cURL, options);
        meta.columns(c).data = stream;
    end
    
    data{i} = meta;
end`

  return (
    <React.Fragment>

    <Typography>
      MATLAB Code
    </Typography>

    <SyntaxHighlighter language="matlab" style={docco}>
      {codeString}
    </SyntaxHighlighter>
    </React.Fragment>
  )
}
