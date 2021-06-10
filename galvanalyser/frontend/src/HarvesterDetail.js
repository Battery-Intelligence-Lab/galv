import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Paper from '@material-ui/core/Paper';
import InputBase from '@material-ui/core/InputBase';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import { useParams } from "react-router-dom";
import IconButton from '@material-ui/core/IconButton';
import TableCell from '@material-ui/core/TableCell';
import MenuItem from '@material-ui/core/MenuItem';
import Select from '@material-ui/core/Select';
import Chip from '@material-ui/core/Chip';
import Container from '@material-ui/core/Container';
import SaveIcon from '@material-ui/icons/Save';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import DeleteIcon from '@material-ui/icons/Delete';
import TableRow from '@material-ui/core/TableRow';
import Files from './Files'
import { Link, useHistory } from "react-router-dom";

import { 
  monitored_paths, add_monitored_path, users, env_harvester,
  update_monitored_path, delete_monitored_path
} from './Api'

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

  useEffect(() => {
    setRow(savedRow);
  }, [savedRow]);

  const rowUnchanged = Object.keys(row).reduce((a, k) => {
    return a && row[k] === savedRow[k];
  }, true);

  let useRow = row;
  if (useRow.monitor_path_id === undefined) {
    useRow = savedRow;
  }

  const setValue = (key) => (e) => {
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
              {selected.map((value) => (
                <Chip key={value} label={value} className={classes.chip} />
              ))}
            </div>
          )}
          MenuProps={MenuProps}
        >
          {userData.map((user) => (
            <MenuItem key={user.username} value={user.username}>
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
          onClick={() => {onRowSave(row);}}
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

export default function HarvesterDetail() {
  const { id } = useParams();
  const classes = useStyles();

  const [userData, setUserData] = useState([])
  const [paths, setPaths] = useState([])
  const [selected, setSelected] = useState({monitor_path_id: null})
  const [envData, setEnvData] = useState([])

  useEffect(() => {
    env_harvester(id).then((response) => {
      if (response.ok) {
        return response.json().then(setEnvData);
      }
      });
  }, []);

  useEffect(() => {
    users().then((response) => {
      if (response.ok) {
        response.json().then(setUserData);
      }
    });
  }, []);

  useEffect(() => {
    refreshPaths(); 
  }, []);

  const refreshPaths= () => {
      monitored_paths(id).then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          setPaths(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
      }
      });
  };

  const addNewPath= () => {
    add_monitored_path({harvester_id: id, path: 'Edit me'}).then(refreshPaths);
  };
  const deletePath = () => {
    delete_monitored_path(selected.monitor_path_id).then(refreshPaths);
  };
  const updatePath = (value) => {
    update_monitored_path(value.monitor_path_id, value).then(refreshPaths);
  };
  
  const isSelected = selected.monitor_path_id !== null;

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
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
    </Paper>
    {isSelected &&
      <Files path={selected}/>
    }
    </Container>
  );
}
