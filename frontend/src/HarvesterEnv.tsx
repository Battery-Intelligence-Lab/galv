// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React, {useState, BaseSyntheticEvent} from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import Connection from "./APIConnection";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";
import {HarvesterFields} from "./Harvesters";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableCell from "@mui/material/TableCell";
import Tooltip from "@mui/material/Tooltip";
import TableRow from "@mui/material/TableRow";
import TableBody from "@mui/material/TableBody";

export type HarvesterEnvProps = {
  harvester: HarvesterFields;
  refreshCallback: () => Promise<void>
  [key: string]: any
}

export default function HarvesterEnv(props: HarvesterEnvProps) {
  const harvester = props.harvester
  const classes = useStyles();
  const [Env, setEnv] = useState<{[key: string]: string}>(props.harvester.environment_variables)
  const [newKey, setNewKey] = useState<string|undefined>()
  const [newValue, setNewValue] = useState<string>("")

  const updateEnv = (data: {[key: string]: string}) => {
    return Connection.fetch<HarvesterFields>(
      props.harvester.url,
      {body: JSON.stringify({environment_variables: data}), method: 'PATCH'}
    )
      .then(r => r.content)
      .then(content => setEnv(content.environment_variables))
      .then(props.refreshCallback)
  };

  const columns = [
    {label: 'Variable', help: 'Environment variable name'},
    {label: 'Value', help: 'Value for the environment variable'},
    {label: 'Actions', help: 'Delete environment variable'},
  ]

  return (
    <Paper className={classes.paper} key={`${harvester.id}_paths`}>
      <Typography variant='h5' p={1}>
        {harvester.name} - monitored paths
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            {columns.map((heading, i) =>
              <TableCell key={`${heading.label}_${i}`}>
                {
                  <Tooltip title={heading.help} placement="top">
                    <Typography>{heading.label}</Typography>
                  </Tooltip>
                }
              </TableCell>
            )}
          </TableRow>
        </TableHead>
        <TableBody>
          {
            Object.keys(Env).map(k =>
              <TableRow key={k}>
                <TableCell key={`${k}-key`}><Typography>{k}</Typography></TableCell>
                <TableCell key={`${k}-value`}>
                  <TextField
                    InputProps={{
                      classes: {
                        input: classes.resize,
                      }
                    }}
                    placeholder="VALUE"
                    value={Env[k]}
                    name="path"
                    onChange={(event: BaseSyntheticEvent) => {
                      if (typeof event.target.value === "string") {
                        updateEnv({...Env, k: event.target.value})
                      }
                    }}
                  />
                </TableCell>
                <TableCell key={`${k}-delete`}>
                  <ActionButtons
                    classes={classes}
                    onDelete={() => {
                      const env = {...Env}
                      delete env[k]
                      updateEnv(env)
                    }}
                  />
                </TableCell>
              </TableRow>
            )
          }
          <TableRow key="new">
            <TableCell key={"new-key"}>
              <TextField
                InputProps={{
                  classes: {
                    input: classes.resize,
                  }
                }}
                placeholder="NEW_VARIABLE"
                helperText="Required"
                value={newKey === undefined? "" : newKey}
                name="path"
                error={newKey !== undefined && !newKey.length}
                onChange={(event) => setNewKey(event.target.value)}
              />
            </TableCell>
            <TableCell key={"new-value"}>
              <TextField
                InputProps={{
                  classes: {
                    input: classes.resize,
                  }
                }}
                placeholder="VALUE"
                value={newValue}
                name="path"
                onChange={(event) => setNewValue(event.target.value)}
              />
            </TableCell>
            <TableCell>
              <ActionButtons
                classes={classes}
                onSave={() => {
                  if (typeof newKey === "string")
                    updateEnv({...Env, [newKey]: newValue})
                      .then(() => {
                        setNewKey(undefined)
                        setNewValue("")
                      })
                }}
                saveIconProps={{component: AddIcon}}
              />
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Paper>
  );
}
