import React, { useEffect, useState, useCallback } from 'react';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Input from '@mui/material/Input';
import InputAdornment from '@mui/material/InputAdornment';
import { makeStyles } from '@mui/styles'
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Chip from '@mui/material/Chip';
import SaveIcon from '@mui/icons-material/Save';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import Files from './Files'

import { 
  monitored_paths, add_monitored_path, users, env_harvester,
  update_monitored_path, delete_monitored_path, isAdmin, 
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

function MyTableRow({env, userData, savedRow, onRowSave, selected, onSelectRow, disableSave, addIcon}) {
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
  if (useRow.id === undefined) {
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

  const Icon = addIcon ? <AddIcon/> : <SaveIcon/> ;

  console.log('userData:', userData.results)

  return (
    <React.Fragment>
    <TableRow 
      onClick={() => {onSelectRow(savedRow);}}
      hover
      selected={selected}
    >
      <TableCell component="th" scope="row">
        {useRow.id}
      </TableCell>
      <TableCell align="right">
        <TextField
          InputProps={{
            classes: {
              input: classes.resize,
            },
            placeholder: "New Monitored Path",
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
          {userData.results.map((user) => (
            <MenuItem key={user.username} value={user.id}>
              {user.username}
            </MenuItem>
          ))}
      </Select>
      </TableCell>
      <TableCell align="right">
        <Tooltip title={addIcon? "Add new Path" : "Save changes to Path"}>
        <span>
        <IconButton
          disabled={disableSave || rowUnchanged} 
          onClick={() => {
            setDirty(false);
            onRowSave(row);
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

export default function HarvesterDetail({harvester}) {
  const classes = useStyles();

  const [userData, setUserData] = useState({results: []})
  const [paths, setPaths] = useState([])
  const [selected, setSelected] = useState({id: null})
  const [envData, setEnvData] = useState([])

  const userIsAdmin = isAdmin();

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
            const results = result.results;
            console.log('Harvester details:', results)
            setPaths(results.sort((arg1, arg2) => arg1.id - arg2.id));
            setSelected(oldSelected => {
              const newSelected = results.find(x => x.id === oldSelected.id);
              return newSelected || {id: null};
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

  const addNewPath = (data) => {
    add_monitored_path({harvester_id: harvester.id, path: data.path}).then(refreshPaths);
  };
  const deletePath = () => {
    delete_monitored_path(selected.id).then(refreshPaths);
  };
  const updatePath = (value) => {
    update_monitored_path(value.id, value).then(refreshPaths);
  };
  
  const isSelected = selected.id !== null;

  return (
    <Paper className={classes.paper}>
    <Typography variant='h5'>
      Harvester "{harvester.name}" monitored paths
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
                key={row.id} 
                env={envData}
                savedRow={row} 
                userData={userData}
                onRowSave={updatePath} 
                selected={selected.id === row.id}
                onSelectRow={setSelected}
                disableSave={!userIsAdmin}
            />
          ))}
          <MyTableRow
              key={'new'}
              env={envData}
              savedRow={{
                id: '',
                harvester_id: harvester.id,
                path: '',
                monitored_for: [],
              }}
              userData={userData}
              onRowSave={addNewPath}
              selected={false}
              onSelectRow={() => {}}
              disableSave={false}
              addIcon={true}
              placeholder={'Add Monitored Path'}
          />
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new path">
      <IconButton 
        aria-label="add" 
        onClick={addNewPath}
        disabled={!userIsAdmin}
      >
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected path">
      <span>
    <IconButton 
      disabled={!userIsAdmin || !isSelected} 
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
