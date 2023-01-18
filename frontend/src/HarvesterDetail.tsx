import React, {useEffect, useState} from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import SaveIcon from '@mui/icons-material/Save';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import PaginatedTable, {RowFunProps} from './PaginatedTable';
import Connection, {User} from "./APIConnection";
import Files from './Files'
import {HarvesterFields} from "./Harvesters";
import UserRoleSet, {UserSet} from "./UserRoleSet";

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

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  function MyTableRow(props: RowFunProps<MonitoredPathFields>) {
    const classes = useStyles();
    const [row, setRow] = useState<MonitoredPathFields>({
      url: "", id: -1, harvester: -1, stable_time: -1, path: '', user_sets: []
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
            <UserRoleSet
              key={`userroleset-${useRow.id}`}
              user_sets={useRow.user_sets}
              last_updated={lastUpdated}
              set_last_updated={setLastUpdated}
            />
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


  const addNewPath = (data: MonitoredPathFields) => {
    const insert_data = {harvester: harvester.id, path: data.path, stable_time: data.stable_time}
    Connection.fetch('monitored_paths/', {body: JSON.stringify(insert_data), method: 'POST'})
      .then(() => setLastUpdated(new Date()))
  };
  const deletePath = () => {
    if (selected !== null)
      Connection.fetch(selected.url, {method: 'DELETE'})
        .then(() => setLastUpdated(new Date()))
  };
  const updatePath = (data: MonitoredPathFields) => {
    const insert_data = {path: data.path, stable_time: data.stable_time}
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

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
            selected={selected !== null && selected.path === row.path}
            onSelectRow={setSelected}
            disableSave={
              Connection.user === null || !row.user_sets.reduce((prev, u) => {
                return prev || (Connection.user !== null && u.users.map(usr => usr.id).includes(Connection.user.id))
              }, false)
            }
          />
        )}
        initial_url={`monitored_paths/?harvester__id=${harvester.id}`}
        new_entry_row={(
          <MyTableRow
            key={"new_path"}
            savedRow={{url: "", id: -1, harvester: harvester.id, path: "", stable_time: 60, user_sets: []}}
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
        selected === null || Connection.user === null || !(
          selected.user_sets.find(u => u.name.toLowerCase() === "harvester admins")?.users.map((u: User) => u.username).includes(Connection.user.username) ||
          selected.user_sets.find(u => u.name.toLowerCase() === "admins")?.users.map((u: User) => u.username).includes(Connection.user.username)
        )
      }
      aria-label="delete"
      onClick={deletePath}
    >
      <DeleteIcon />
    </IconButton>
      </span>
      </Tooltip>
      {selected !== null && <Files path={selected} lastUpdated={lastUpdated}/>}
    </Paper>

  );
}
