import React, {useState} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs';
import Typography from '@mui/material/Typography';
import Connection from "./APIConnection";


export default function GetDatasetMatlab({dataset}) {
  const [token, setToken] = useState(Connection.user?.token || 'API_TOKEN');

  let domain = window.location.href.split('/')[2];
  domain = domain.split(':')[0]

  const host = `http://api.${domain}`
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
% SPDX-License-Identifier: BSD-2-Clause
% Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
% of Oxford, and the 'Galvanalyser' Developers. All rights reserved.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% login to galvanalyser > Generate API Token
token = '4244dc4e49acf8eebe4ea134d37d789f9cb1e359c9b09ca3e862288ddfb6831b';
apiURL = 'http://api.galvanalyser.oxrse.uk/datasets';
options = weboptions('HeaderFields', {'Authorization' ['Bearer ' token]});

% Datasets can be referenced by name or by id. 
% Only the id is guaranteed to be unique.
% You can add in additional dataset_names or dataset_ids to also
% fetch the contents of those datasets.
dataset_names = [];
dataset_ids = [3, 4]; % add additional dataset ids here if required

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% look up dataset ids if names provided
if exist('dataset_names', 'var') && ~ isempty(dataset_names)
    dataset_meta = webread(apiURL, options);
    dataset_ids = [dataset_ids dataset_meta(ismember({dataset_meta.name}, dataset_names)).id];
end

dataset_ids = string(dataset_ids(:));
dataset_ids = unique(dataset_ids);

data(1, length(dataset_ids)) = struct();

for i = 1:length(dataset_ids)
    d = dataset_ids(i);
    
    % get data
    dsURL = strcat(apiURL, '/', d, '/');
    meta = webread(dsURL, options);

    col_data = {};
    
    % append column data in columns
    for c = 1:length(meta.columns)
        cURL = meta.columns{c};
        stream = webread(cURL, options);
        meta.column_details{c} = stream;
        column_content = webread(stream.values, options);
        % drop final newline
        column_content = regexprep(column_content, '\n$', '');
        column_content = strsplit(column_content, '\n');
        column_content = arrayfun(@(c) str2num(c{1}), column_content);
        col_data{c} = column_content;
    end
    data(i).columns = col_data;
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
