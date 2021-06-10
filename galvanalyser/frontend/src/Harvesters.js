import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Paper from '@material-ui/core/Paper';
import InputBase from '@material-ui/core/InputBase';
import PlayArrowIcon from '@material-ui/icons/PlayArrow';
import Tooltip from '@material-ui/core/Tooltip';
import ListIcon from '@material-ui/icons/List';
import AddIcon from '@material-ui/icons/Add';
import IconButton from '@material-ui/core/IconButton';
import SettingsIcon from '@material-ui/icons/Settings';
import TableCell from '@material-ui/core/TableCell';
import Container from '@material-ui/core/Container';
import SaveIcon from '@material-ui/icons/Save';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import DeleteIcon from '@material-ui/icons/Delete';
import TableRow from '@material-ui/core/TableRow';
import { Link, useHistory } from "react-router-dom";

import HarvesterDetail from './HarvesterDetail';
import { 
  run_harvester, harvesters, add_harvester, 
  update_harvester, delete_harvester
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
  iconButton: {
    padding: 10,
  },
}));

function MyTableRow({savedRow, onRowSave, selected, onSelectRow}) {
  const classes = useStyles();
  const [row, setRow] = useState([])

  useEffect(() => {
    setRow(savedRow);
  }, [savedRow]);

  const rowUnchanged = row.machine_id === savedRow.machine_id;
  let useRow = row;
  if (useRow.id === undefined) {
    useRow = savedRow;
  }

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
          }}
          value={useRow.machine_id}
          onChange={(e) => {
            setRow({...row, machine_id: e.target.value});
          }} 
        >
        </TextField>
      </TableCell>
      <TableCell component="th" scope="row">
        {useRow.harvester_name}
      </TableCell>
      <TableCell component="th" scope="row">
        {useRow.last_successful_run}
      </TableCell>
      <TableCell component="th" scope="row">
        {useRow.periodic_hour}
      </TableCell>
      <TableCell align="right">
        <Tooltip title="Save changes to harvester">
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

export default function Harvesters() {
  const classes = useStyles();

  const [harvesterData, setHarvesterData] = useState([])
  const [selected, setSelected] = useState({id: null})

  useEffect(() => {
    refreshHarvesters(); 
  }, []);

  const refreshHarvesters= () => {
      harvesters().then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          setHarvesterData(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
      }
      });
  };

  const addNewHarvester = () => {
    add_harvester({machine_id: 'Edit me'}).then(refreshHarvesters);
  };
  const deleteHarvester= () => {
    delete_harvester(selected.id).then(refreshHarvesters);
  };
  const updateHarvester= (value) => {
    update_harvester(value.id, value).then(refreshHarvesters);
  };
  
  const isSelected = selected.id !== null;
  let history = useHistory();

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
    <TableContainer>
      <Table className={classes.table} size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell align="right">Machine</TableCell>
            <TableCell align="right">Harvester</TableCell>
            <TableCell align="right">Last Completed Run</TableCell>
            <TableCell align="right">Periodic</TableCell>
            <TableCell align="right">Save</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {harvesterData.map((row) => (
            <MyTableRow 
                key={row.id} 
                savedRow={row} 
                onRowSave={updateHarvester} 
                selected={selected.id === row.id}
                onSelectRow={setSelected}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new harvester">
      <IconButton aria-label="add" onClick={addNewHarvester}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected harvester">
      <span>
    <IconButton disabled={!isSelected} aria-label="delete" onClick={deleteHarvester}>
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    <Tooltip title="Paths and files for selected harvester">
      <span>
      <IconButton disabled={!isSelected} onClick={()=>{history.push(`/harvester/${selected.id}`);}}>
      <ListIcon/>
    </IconButton>
    </span>
    </Tooltip>
    <Tooltip title="Run the selected harvester">
      <span>
      <IconButton disabled={!isSelected} onClick={()=>{run_harvester(selected.id)}}>
      <PlayArrowIcon/>
    </IconButton>
    </span>
    </Tooltip>


    </Paper>
    </Container>
  );
}
