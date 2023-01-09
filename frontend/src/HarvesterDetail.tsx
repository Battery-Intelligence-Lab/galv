import React, {useEffect, useState, useCallback, ChangeEvent} from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Input from '@mui/material/Input';
import InputAdornment from '@mui/material/InputAdornment';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Chip from '@mui/material/Chip';
import SaveIcon from '@mui/icons-material/Save';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import PaginatedTable, {RowFunProps} from './PaginatedTable';
import Connection, {User} from "./APIConnection";
import Files from './Files'

import {
  monitored_paths, add_monitored_path, users, env_harvester,
  update_monitored_path, delete_monitored_path, isAdmin, url,
} from './Api'
import {HarvesterFields} from "./Harvesters";

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

type MonitoredPathUserGroups = {
  harvester_admins: User[];
  admins: User[];
  users: User[];
}

export type MonitoredPathFields = {
  url: string;
  harvester: number;
  stable_time: number;
  path: string;
  users: MonitoredPathUserGroups;
}

function MyTableRow(props: RowFunProps<MonitoredPathFields>) {
  const classes = useStyles();
  const [row, setRow] = useState<MonitoredPathFields>({
    url: "", harvester: -1, stable_time: -1, path: '', users: {harvester_admins: [], admins: [], users: []}
  })
  const [dirty, setDirty] = useState<boolean>(false)

  const rowUnchanged = Object.keys(row).reduce((a, k) => {
    //@ts-ignore
    return a && row[k] === props.savedRow[k];
  }, true);

  useEffect(() => {
    if (!dirty && props.savedRow) {
      setRow(props.savedRow);
    }
  }, [dirty, props.savedRow]);

  let useRow = row;
  if (row.harvester === -1 && props.savedRow)
    useRow = props.savedRow;

  const setValue = (key: string) => (e: any) => {
    setDirty(true);
    setRow({...useRow, [key]: e.target?.value});
  };

  const Icon = props.addIcon ? <AddIcon/> : <SaveIcon/> ;

  return (
    <React.Fragment>
      <TableRow
        onClick={() => {props.onSelectRow(props.savedRow);}}
        hover
        selected={props.selected}
      >
        <TableCell align="right" key={"Path"}>
          <TextField
            InputProps={{
              classes: {
                input: classes.resize,
              },
              placeholder: "New Monitored Path",
              // TODO: Handle harvester base paths
              // startAdornment: <InputAdornment
              //                   className={classes.inputAdornment}
              //                   position="start">
              //                   {env.GALVANALYSER_HARVESTER_BASE_PATH}/
              //                 </InputAdornment>,
            }}
            value={useRow.path}
            onChange={setValue('path')} />
        </TableCell>
        <TableCell>
          <TextField
            type="number"
            placeholder="60"
            InputProps={{
              classes: {
                input: classes.resize,
              },
            }}
            value={useRow.stable_time ? useRow.stable_time : ''}
            onChange={(e) => {
              setDirty(true);
              setRow({...row, stable_time: parseInt(e.target.value)});
            }}
          >
          </TextField>
        </TableCell>
        <TableCell align="right" key={"Users"}>
          Harvester Admins:<br/>
          {useRow.users.harvester_admins.map(u => (<span className="harvester_admin">{u.username}</span>))}
          Admins:<br/>
          {useRow.users.admins.map(u => (<span className="admin">{u.username}</span>))}
          Users:<br/>
          {useRow.users.users.map(u => (<span className="user">{u.username}</span>))}
        </TableCell>
        <TableCell align="right" key={"Save"}>
          <Tooltip title={props.addIcon? "Add new Path" : "Save changes to Path"}>
        <span>
        <IconButton
          disabled={props.disableSave || rowUnchanged}
          onClick={() => {
            setDirty(false);
            props.onRowSave(row);
          }}
        >
          {Icon}
        </IconButton>
        </span>
          </Tooltip>
        </TableCell>
      </TableRow>
    </React.Fragment>
  )
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

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const addNewPath = (data: MonitoredPathFields) => {
    const insert_data = {harvester: harvester.id, path: data.path, stable_time: data.stable_time}
    Connection.fetch('monitored_paths/', {body: JSON.stringify(insert_data), method: 'POST'})
      .then(() => setLastUpdated(new Date()))
  };
  const deletePath = () => {
    if (isSelected)
      Connection.fetch(selected.url, {method: 'DELETE'})
        .then(() => setLastUpdated(new Date()))
  };
  const updatePath = (data: MonitoredPathFields) => {
    const insert_data = {path: data.path, stable_time: data.stable_time}
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

  const isSelected = selected !== null;

  const column_headings = [
    {label: 'Path', help: 'Directory to watch'},
    {label: 'Stable Time (s)', help: 'Seconds files must remain unchanged to be considered stable and imported'},
    {label: 'Users', help: 'Users with access to this path\'s datasets'},
    {label: 'Save', help: 'Click to save edits to a row'},
  ]

  const table_head = column_headings.map(heading => (
    <TableCell key={heading.label}>
      <Tooltip title={heading.help}>
        <Typography>
          {heading.label}
        </Typography>
      </Tooltip>
    </TableCell>
  ))

  return (
    <Paper className={classes.paper} key={`${harvester.id}_paths`}>
      <Typography variant='h5'>
        Harvester "{harvester.name}" monitored paths
      </Typography>
      <PaginatedTable
        key={`${harvester.id}_paths`}
        header={(<TableHead>{table_head}</TableHead>)}
        row_fun={(row: MonitoredPathFields) => (
          <MyTableRow
            key={row.path}
            savedRow={row}
            onRowSave={updatePath}
            selected={isSelected && selected.path === row.path}
            onSelectRow={setSelected}
            disableSave={
              Connection.user === null || !(
                row.users.harvester_admins.map((u: User) => u.username).includes(Connection.user.username) ||
                row.users.admins.map((u: User) => u.username).includes(Connection.user.username) ||
                row.users.users.map((u: User) => u.username).includes(Connection.user.username)
              )
            }
          />
        )}
        initial_url={`monitored_paths/?harvester__id=${harvester.id}`}
        new_entry_row={(
          <MyTableRow
            key={"new_path"}
            savedRow={{
              url: "", harvester: harvester.id, path: "", stable_time: 60,
              users: {harvester_admins: [], admins: [], users: []}
            }}
            onRowSave={addNewPath}
            selected={false}
            onSelectRow={() => {
            }}
            disableSave={false}
          />
        )}
        styles={classes}
        last_updated={lastUpdated}
      />
      <Tooltip title="Delete selected path">
      <span>
    <IconButton
      disabled={
        !isSelected || Connection.user === null || !(
          selected.users.harvester_admins.map((u: User) => u.username).includes(Connection.user.username) ||
          selected.users.admins.map((u: User) => u.username).includes(Connection.user.username)
        )
      }
      aria-label="delete"
      onClick={deletePath}
    >
      <DeleteIcon />
    </IconButton>
      </span>
      </Tooltip>
      {isSelected &&
          <Files path={selected}/>
      }
    </Paper>

  );
}
