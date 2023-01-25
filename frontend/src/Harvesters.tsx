import React, { useState, Fragment } from 'react';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import SearchIcon from '@mui/icons-material/Search';
import DeleteIcon from '@mui/icons-material/Delete';

import HarvesterDetail from './HarvesterDetail';
import Connection from "./APIConnection";
import {UserSet} from "./UserRoleSet";
import AsyncTable, {Column} from "./AsyncTable";

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

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  table: {
    minWidth: 650,
  },
  resize: {
    fontSize: '11pt',
  },
  input: {
    marginLeft: theme.spacing(1),
    flex: 1,
  },
  iconButton: {
    padding: 10,
  },
  paper: {}
}));

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
    {label: 'Details', help: 'View harvester path information'},
    {label: 'Save', help: 'Click to save edits to a row'},
    {label: 'Delete', help: 'Delete a harvester'},
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        {<AsyncTable
          columns={columns}
          rows={[
            (row: any) => <Fragment key="id"><Typography>{row.id}</Typography></Fragment>,
            (row: any, context) => <Fragment key="name">
              <TextField
                InputProps={{classes: {input: classes.resize}}}
                value={row.name}
                name="name"
                onChange={context.update}
              >
              </TextField>
            </Fragment>,
            (row: any) => <Fragment key="last_check_in">
              {
                (row.last_check_in &&
                  Intl.DateTimeFormat(
                    'en-GB',
                    { dateStyle: 'long', timeStyle: 'long' })
                    .format(Date.parse(row.last_check_in))
                ) || (<Typography color='grey'>None</Typography>)
              }
            </Fragment>,
            (row: any, context) => <Fragment key="sleep_time">
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
            (row: any) => <Fragment key="select">
              <IconButton onClick={() => selected?.id === row.id? setSelected(null) : setSelected(row)}>
                <SearchIcon color={selected?.id === row.id? 'info' : undefined} />
              </IconButton>
            </Fragment>,
            (row: any, context) => <Fragment key="save">
              <IconButton
                disabled={!userIsAdmin(row) || !row._changed}
                onClick={() => updateHarvester(row).then(context.refresh)}
              >
                <SaveIcon />
              </IconButton>
            </Fragment>,
            (row: any, context) => <Fragment key="delete">
              <IconButton
                disabled={!userIsAdmin(row)}
                aria-label="delete"
                onClick={() => deleteHarvester(row).then(context.refresh)}
              >
                <DeleteIcon/>
              </IconButton>
            </Fragment>,
          ]}
          initial_url="harvesters/?all=true"
        />}
      </Paper>
      {selected !== null && <HarvesterDetail harvester={selected} />}
    </Container>
  );
}
