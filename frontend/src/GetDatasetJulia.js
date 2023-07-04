import React, {useState, useEffect} from "react";
import SyntaxHighlighter from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/cjs/styles/hljs';
import Typography from '@mui/material/Typography';
import Connection from "./APIConnection";
import {CircularProgress} from "@mui/material";


export default function GetDatasetJulia({dataset}) {
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
                <SyntaxHighlighter language="julia" style={docco}>{
                    `# SPDX-License-Identifier: BSD-2-Clause
# Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
# of Oxford, and the 'Galv' Developers. All rights reserved.

using HTTP
using JSON

host = "${host}"
headers = Dict{String, String}("Authorization" => "Bearer ${token}")

# Configuration
verbose = true

dataset_ids = [${dataset.id}]
dataset_metadata = Dict{Int64, Dict{String, Any}}()
column_metadata = Dict{Int64, Dict{Int64, Any}}()
datasets = Dict{Int64, DataFrame}()

function vprintln(s)
    if verbose
        println(s)
    end
end

function get_column_values(dataset_id, column)
    url = column["values"]
    if url == ""
        return
    end

    column_name = column["name"]
    dtype = column["data_type"]

    vprintln("Downloading values for column $dataset_id:$column_name [$url]")
    
    response = HTTP.request("GET", url, headers)
    
    try
        body = String(response.body)
        str_values = split(body, '\\n')
        values = Vector{String}(str_values[begin:end-1])
        if dtype == "float"
            return map((x -> parse(Float64, x)), values)
        elseif dtype == "int"
            return map((x -> parse(Int64, x)), values)
        else
            return convert(String, values)
        end
    catch
        println("Error parsing values $dataset_id:$column_name [$url]")
        return
    end

end

function get_column(dataset_id, url)
    vprintln("Downloading column $url")
    
    response = HTTP.request("GET", url, headers)
    column = Dict{String, Any}()
    
    try
        column = JSON.parse(String(response.body))
    catch
        println("Error parsing JSON for column $url")
        return
    end
    
    # Download column values
    values = get_column_values(dataset_id, column)
    pop!(column, "values", "")

    datasets[dataset_id][!, column["name"]] = values

    return column
end

function get_dataset(id)
    vprintln("Downloading dataset $id")
    
    response = HTTP.request("GET", "$host/datasets/$id", headers)
    body = Dict{String, Any}()

    try
        body = JSON.parse(String(response.body))
    catch
        println("Error parsing JSON for dataset $id")
        return
    end
    dataset_metadata[id] = body
    
    # Download columns
    columns = dataset_metadata[id]["columns"]
    len = length(columns)
    vprintln("Downloading $len columns for dataset $id")

    datasets[id] = DataFrame()
    column_metadata[id] = Dict{Int64, Any}()
    
    for (i, col) in enumerate(columns)
        timings = @timed column = get_column(id, col)
        column_metadata[id][i] = column
        n = column["name"]
        s = round(timings.time, digits = 2)
        vprintln("Column $n completed in $s seconds")
    end

    vprintln("Completed.")
end

for id in dataset_ids
    timings = @timed get_dataset(id)
    s = round(timings.time, digits = 2)
    vprintln("Completed dataset $id in $s seconds")
end

vprintln("All datasets complete.")

`
                }</SyntaxHighlighter>
            )
    }, [columns, dataset.id, host, token])

    return (
        <React.Fragment>
            <Typography>
                Julia Code
            </Typography>

            {code}
        </React.Fragment>
    )
}
