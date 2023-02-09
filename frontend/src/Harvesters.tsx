import React, { useState, Fragment } from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import HarvesterDetail from './HarvesterDetail';
import Connection from "./APIConnection";
import {UserSet} from "./UserRoleSet";
import AsyncTable, {Column} from "./AsyncTable";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";

export type HarvesterWriteableFields = {
  name: string;
  sleep_time: number;
}

export type HarvesterFields = HarvesterWriteableFields & {
  url: string;
  id: number;
  last_check_in: string | null;
  user_sets: UserSet[];
}

export default function Harvesters() {
  const classes = useStyles();

  const [selected, setSelected] = useState<HarvesterFields|null>(null)
  const userIsAdmin = (harvester: HarvesterFields) =>
    Connection.user !== null &&
    harvester?.user_sets?.find(u => u.name.toLowerCase() === 'admins')?.users
      .map(usr => usr.username)
      .includes(Connection.user.username)

  const updateHarvester = (data: HarvesterFields) => {
    console.log('updateHarvester', data)
    const insert_data: HarvesterWriteableFields = {
      name: data.name,
      sleep_time: data.sleep_time
    }
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const deleteHarvester = (harvester: HarvesterFields) => Connection.fetch(harvester.url, {method: 'DELETE'})

  const columns: Column[] = [
    {label: 'ID', help: 'Harvester id in database'},
    {label: 'Name', help: 'Harvester name'},
    {label: 'Last Check In', help: 'Datetime of last harvester run that successfully contacted the database'},
    {label: 'Sleep Time (s)', help: 'Time harvester waits after completing a cycle before beginning the next'},
    {label: 'Actions', help: 'Inspect / Add / Save / Delete harvester path information'}
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        {<AsyncTable<HarvesterFields>
          columns={columns}
          row_generator={(row, context) => [
            <Fragment key="id"><Typography>{row.id}</Typography></Fragment>,
            <Fragment key="name">
              <TextField
                InputProps={{classes: {input: classes.resize}}}
                value={row.name}
                name="name"
                onChange={context.update}
              >
              </TextField>
            </Fragment>,
            <Fragment key="last_check_in">
              {
                (row.last_check_in &&
                  Intl.DateTimeFormat(
                    'en-GB',
                    { dateStyle: 'long', timeStyle: 'long' })
                    .format(Date.parse(row.last_check_in))
                ) || (<Typography color='grey'>None</Typography>)
              }
            </Fragment>,
            <Fragment key="sleep_time">
              <TextField
                type="number"
                placeholder="60"
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                value={row.sleep_time || ''}
                name="sleep_time"
                onChange={context.update}
              >
              </TextField>
            </Fragment>,
            <Fragment key="actions">
              <ActionButtons
                classes={classes}
                onInspect={() => selected?.id === row.id? setSelected(null) : setSelected(row)}
                inspectIconProps={selected?.id === row.id ? {color: 'info'} : {}}
                onSave={() => updateHarvester(row).then(context.refresh)}
                saveButtonProps={{disabled: !userIsAdmin(row) || !context.value_changed}}
                onDelete={() => window.confirm(`Delete ${row.name}?`) && deleteHarvester(row).then(context.refresh)}
                deleteButtonProps={{disabled: !userIsAdmin(row)}}
              />
            </Fragment>,
          ]}
          url="harvesters/?all=true"
        />}
      </Paper>
      {selected !== null && <HarvesterDetail harvester={selected} />}
    </Container>
  );
}
