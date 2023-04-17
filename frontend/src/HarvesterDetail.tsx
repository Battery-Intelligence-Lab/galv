// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React, {useState, Fragment} from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import Connection from "./APIConnection";
import Files from './Files'
import {HarvesterFields} from "./Harvesters";
import UserRoleSet, {UserSet} from "./UserRoleSet";
import AsyncTable from "./AsyncTable";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";

export type MonitoredPathFields = {
  url: string;
  id: number;
  harvester: number;
  stable_time: number;
  path: string;
  user_sets: UserSet[];
}
export type HarvesterDetailProps = {
  harvester: HarvesterFields,
  [key: string]: any
}

export default function HarvesterDetail(props: HarvesterDetailProps) {
  const harvester = props.harvester
  const classes = useStyles();

  const [selected, setSelected] = useState<MonitoredPathFields|null>(null)

  const addNewPath = (data: MonitoredPathFields) => {
    const insert_data = {harvester: harvester.url, path: data.path, stable_time: data.stable_time}
    return Connection.fetch('monitored_paths/', {body: JSON.stringify(insert_data), method: 'POST'})
  };
  const deletePath = (data: MonitoredPathFields) => Connection.fetch(data.url, {method: 'DELETE'})

  const updatePath = (data: MonitoredPathFields) => {
    const insert_data = {path: data.path, stable_time: data.stable_time}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(r => r.content)
  };

  const columns = [
    {label: 'Path', help: 'Directory to watch'},
    {label: 'Stable Time (s)', help: 'Seconds files must remain unchanged to be considered stable and imported'},
    {label: 'Users', help: 'Users with access to this path\'s datasets'},
    {label: 'Actions', help: 'Inspect / Save / Delete monitored path (imported datasets will remain)'},
  ]

  return (
    <Paper className={classes.paper} key={`${harvester.id}_paths`}>
      <Typography variant='h5' p={1}>
        {harvester.name} - monitored paths
      </Typography>
      <AsyncTable<MonitoredPathFields>
        classes={classes}
        key={`${harvester.id}_paths`}
        columns={columns}
        row_generator={(row, context) => [
          <Fragment>
            <TextField
              InputProps={{
                classes: {
                  input: classes.resize,
                }
              }}
              placeholder="/new/directory/path"
              value={row.path}
              name="path"
              onChange={context.update}
            />
          </Fragment>,
          <Fragment>
            <TextField
              type="number"
              InputProps={{
                classes: {
                  input: classes.resize,
                },
              }}
              value={row.stable_time ? row.stable_time : ''}
              name="stable_time"
              onChange={context.update}
            >
            </TextField>
          </Fragment>,
          context.is_new_row? <Fragment key="users" /> : <Fragment>
            <UserRoleSet
              key={`userroleset-${row.id}`}
              user_sets={row.user_sets}
              last_updated={new Date()}
              set_last_updated={() => context.refresh_all_rows(false)}
            />
          </Fragment>,
          <Fragment key="actions">
            <ActionButtons
              classes={classes}
              onInspect={() => selected?.id === row.id? setSelected(null) : setSelected(row)}
              inspectButtonProps={{disabled: context.is_new_row}}
              inspectIconProps={selected?.id === row.id ? {color: 'info'} : {}}
              onSave={
                context.is_new_row?
                  () => addNewPath(row).then(() => context.refresh_all_rows()) :
                  () => updatePath(row).then(context.refresh)
              }
              saveButtonProps={{disabled: !context.value_changed}}
              saveIconProps={{component: context.is_new_row? AddIcon : SaveIcon}}
              onDelete={() => window.confirm(`Delete ${row.path}?`) && deletePath(row).then(context.refresh)}
              deleteButtonProps={{disabled: context.is_new_row}}
            />
          </Fragment>
        ]}
        url={`monitored_paths/?harvester__id=${harvester.id}`}
        new_row_values={{path: "", stable_time: 60}}
        styles={classes}
      />
      {selected !== null && <Files path={selected} />}
    </Paper>
  );
}
