import React, { useEffect, useState, useCallback } from 'react';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Paper from '@material-ui/core/Paper';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import IconButton from '@material-ui/core/IconButton';
import TableCell from '@material-ui/core/TableCell';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Chip from '@material-ui/core/Chip';
import SaveIcon from '@material-ui/icons/Save';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import DeleteIcon from '@material-ui/icons/Delete';
import TableRow from '@material-ui/core/TableRow';
import Files from './Files'

import { 
  monitored_paths, add_monitored_path, users, env_harvester,
  update_monitored_path, delete_monitored_path
} from './Api'

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

function MyTableRow({env, userData, savedRow, onRowSave, selected, onSelectRow}) {
  const classes = useStyles();
  const [row, setRow] = useState([])
  const [dirty, setDirty] = useState(false)

  const rowUnchanged = Object.keys(row).reduce((a, k) => {
    return a && row[k] === savedRow[k];
  }, true);

  useEffect(() => {
    if (!dirty) { 
      setRow(savedRow);
    }
  }, [dirty, savedRow]);



  let useRow = row;
  if (useRow.monitor_path_id === undefined) {
    useRow = savedRow;
  }

  const setValue = (key) => (e) => {
    setDirty(true);
    setRow({...useRow, [key]: e.target.value});
  };

  const ITEM_HEIGHT = 48;
  const ITEM_PADDING_TOP = 8;
  const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };

  const idToName = (id) => {
    const user = userData.find((x) => x.id === id);
    return user ? user.username : 'Not Found';
  };

  return (
    <React.Fragment>
    <TableRow 
      onClick={() => {onSelectRow(savedRow);}}
      hover
      selected={selected}
    >
      <TableCell component="th" scope="row">
        {useRow.monitor_path_id}
      </TableCell>
      <TableCell align="right">
        <TextField
          InputProps={{
            classes: {
              input: classes.resize,
            },
            startAdornment: <InputAdornment 
                              className={classes.inputAdornment} 
                              position="start">
                              {env.GALVANALYSER_HARVESTER_BASE_PATH}/
                            </InputAdornment>,
          }}
          value={useRow.path}
          onChange={setValue('path')} />
      </TableCell>
      <TableCell align="right">
      <Select
          multiple
          value={useRow.monitored_for}
          onChange={setValue('monitored_for')}
          input={<Input/>}
          renderValue={(selected) => (
            <div className={classes.chips}>
              {selected.map((id) => (
                <Chip key={id} label={idToName(id)} className={classes.chip} />
              ))}
            </div>
          )}
          MenuProps={MenuProps}
        >
          {userData.map((user) => (
            <MenuItem key={user.username} value={user.id}>
              {user.username}
            </MenuItem>
          ))}
      </Select>
      </TableCell>
      <TableCell align="right">
        <Tooltip title="Save changes to path">
        <span>
        <IconButton
          disabled={rowUnchanged} 
          onClick={() => {
            setDirty(false);
            onRowSave(row);
          }}
        >
          <SaveIcon />
        </IconButton>
        </span>
        </Tooltip>
      </TableCell>
    </TableRow>
    </React.Fragment>
  )
}

export default function HarvesterDetail({harvester}) {
  const classes = useStyles();

  const [userData, setUserData] = useState([])
  const [paths, setPaths] = useState([])
  const [selected, setSelected] = useState({monitor_path_id: null})
  const [envData, setEnvData] = useState([])

  useEffect(() => {
    env_harvester(harvester.id).then((response) => {
      if (response.ok) {
        return response.json().then(setEnvData);
      }
      });
  }, [harvester.id]);

  useEffect(() => {
    users().then((response) => {
      if (response.ok) {
        response.json().then(setUserData);
      }
    });
  }, []);

  const refreshPaths = useCallback(
    () => {
      monitored_paths(harvester.id).then((response) => {
        if (response.ok) {
          return response.json().then((result) => {
            setPaths(result.sort((arg1, arg2) => arg1.monitor_path_id - arg2.monitor_path_id));
            setSelected(oldSelected => {
              const newSelected = result.find(x => x.monitor_path_id === oldSelected.monitor_path_id);
              return newSelected || {monitor_path_id: null};
            });
          });
        }
      });
    },
    [harvester.id],
  );

  useEffect(() => {
    refreshPaths(); 
  }, [harvester, refreshPaths]);

  const addNewPath= () => {
    add_monitored_path({harvester_id: harvester.id, path: 'Edit me'}).then(refreshPaths);
  };
  const deletePath = () => {
    delete_monitored_path(selected.monitor_path_id).then(refreshPaths);
  };
  const updatePath = (value) => {
    update_monitored_path(value.monitor_path_id, value).then(refreshPaths);
  };
  
  const isSelected = selected.monitor_path_id !== null;

  return (
    <Paper className={classes.paper}>
    <Typography variant='h5'>
      Harvester "{harvester.machine_id}" monitored paths
    </Typography>
    <TableContainer>
      <Table className={classes.table} size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell align="right">Path</TableCell>
            <TableCell align="right">Users</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {paths.map((row) => (
            <MyTableRow 
                key={row.monitor_path_id} 
                env={envData}
                savedRow={row} 
                userData={userData}
                onRowSave={updatePath} 
                selected={selected.monitor_path_id === row.monitor_path_id}
                onSelectRow={setSelected}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new path">
      <IconButton aria-label="add" onClick={addNewPath}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected path">
      <span>
    <IconButton disabled={!isSelected} aria-label="delete" onClick={deletePath}>
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
