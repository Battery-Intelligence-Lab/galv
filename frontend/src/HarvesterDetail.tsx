import React, {useState, Fragment} from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import Connection from "./APIConnection";
import Files from './Files'
import {HarvesterFields} from "./Harvesters";
import UserRoleSet, {UserSet} from "./UserRoleSet";
import AsyncTable from "./AsyncTable";
import SearchIcon from "@mui/icons-material/Search";

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(4),
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
  inputAdornment: {
    color: theme.palette.text.disabled,
  },
  iconButton: {
    padding: 10,
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  chip: {
    margin: 2,
  },
}));

export type MonitoredPathFields = {
  url: string;
  id: number;
  harvester: number;
  stable_time: number;
  path: string;
  user_sets: UserSet[];
}
type HarvesterDetailProps = {
  harvester: HarvesterFields,
  [key: string]: any
}

// TODO: Figure out why we get unique key errors
export default function HarvesterDetail(props: HarvesterDetailProps) {
  const harvester = props.harvester
  const classes = useStyles();

  const [selected, setSelected] = useState<MonitoredPathFields|null>(null)

  const addNewPath = (data: MonitoredPathFields) => {
    const insert_data = {harvester: harvester.id, path: data.path, stable_time: data.stable_time}
    return Connection.fetch('monitored_paths/', {body: JSON.stringify(insert_data), method: 'POST'})
  };
  const deletePath = (data: MonitoredPathFields) => Connection.fetch(data.url, {method: 'DELETE'})

  const updatePath = (data: MonitoredPathFields) => {
    const insert_data = {path: data.path, stable_time: data.stable_time}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const columns = [
    {label: 'Path', help: 'Directory to watch'},
    {label: 'Stable Time (s)', help: 'Seconds files must remain unchanged to be considered stable and imported'},
    {label: 'Users', help: 'Users with access to this path\'s datasets'},
    {label: 'Files', help: 'View files in this directory'},
    {label: 'Save', help: 'Save changes'},
    {label: 'Delete', help: 'Delete monitored path (imported datasets will remain)'},
  ]

  return (
    <Paper className={classes.paper} key={`${harvester.id}_paths`}>
      <Typography variant='h5'>
        {harvester.name} - monitored paths
      </Typography>
      <AsyncTable<MonitoredPathFields>
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
              set_last_updated={context.refresh}
            />
          </Fragment>,
          context.is_new_row? <Fragment key="select"/> : <Fragment key="select">
            <IconButton onClick={() => selected?.id === row.id? setSelected(null) : setSelected(row)}>
              <SearchIcon color={selected?.id === row.id? 'info' : undefined} />
            </IconButton>
          </Fragment>,
          <Fragment key="save">
            <IconButton
              disabled={!context.value_changed}
              onClick={
                context.is_new_row?
                  () => addNewPath(row).then(context.refresh_all_rows) :
                  () => updatePath(row).then(context.refresh)
              }
            >
              {context.is_new_row? <AddIcon/> : <SaveIcon/>}
            </IconButton>
          </Fragment>,
          context.is_new_row? <Fragment key="delete"/> : <Fragment key="delete">
            <IconButton
              aria-label="delete"
              onClick={() => deletePath(row).then(context.refresh)}
            >
              <DeleteIcon/>
            </IconButton>
          </Fragment>,
        ]}
        url={`monitored_paths/?harvester__id=${harvester.id}&all=true`}
        new_row_values={{path: "", stable_time: 60}}
        styles={classes}
      />
      {selected !== null && <Files path={selected} />}
    </Paper>
  );
}
