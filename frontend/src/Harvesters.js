import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';

import HarvesterDetail from './HarvesterDetail';
import { 
  run_harvester, harvesters, add_harvester, 
  update_harvester, delete_harvester, isAdmin 
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

function MyTableRow({savedRow, onRowSave, selected, onSelectRow, disableSave}) {
  const classes = useStyles();
  const [row, setRow] = useState([])
  const [dirty, setDirty] = useState(false)

  useEffect(() => {
    if (!dirty) { 
      setRow(savedRow);
    }
  }, [dirty, savedRow]);


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
        {savedRow.id}
      </TableCell>
      
      <TableCell>
        <TextField
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          value={useRow.machine_id}
          onChange={(e) => {
            setDirty(true);
            setRow({...row, machine_id: e.target.value});
          }} 
        >
        </TextField>
      </TableCell>
      <TableCell component="th" scope="row">
        {savedRow.harvester_name}
      </TableCell>
      <TableCell component="th" scope="row">
        {savedRow.is_running &&
          (<Typography color='secondary'>True</Typography>)
        }
      </TableCell>
      <TableCell component="th" scope="row">
        {savedRow.last_successful_run && 
          Intl.DateTimeFormat('en-GB', 
          { dateStyle: 'long', timeStyle: 'long' }).format(
          Date.parse(savedRow.last_successful_run)
        )}
      </TableCell>
      <TableCell>
        <TextField
          type="number"
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          value={useRow.periodic_hour ? useRow.periodic_hour : ''}
          onChange={(e) => {
            setDirty(true);
            setRow({...row, periodic_hour: e.target.value});
          }} 
        >
        </TextField>
      </TableCell>
      <TableCell align="right">
        <Tooltip title="Save changes to harvester">
        <span>
        <IconButton
          disabled={disableSave || !dirty} 
          onClick={() => {
            onRowSave(row);
            setDirty(false);
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

export default function Harvesters() {
  const classes = useStyles();

  const [harvesterData, setHarvesterData] = useState([])
  const [selected, setSelected] = useState({id: null})
  const userIsAdmin = isAdmin()

  useEffect(() => {
    refreshHarvesters();
    const interval = setInterval(() => {
      // refreshHarvesters();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const refreshHarvesters= () => {
      harvesters().then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          const results = result.results;
          setHarvesterData(results.sort((arg1, arg2) => arg1.id - arg2.id));
          setSelected(oldSelected => {
            const newSelected = results.find(x => x.id === oldSelected.id)
            return newSelected || {id: null};
          });
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

  const runSelectedHarvester = () => {
    run_harvester(selected.id).then(refreshHarvesters);
  };

  
  const isSelected = selected.id !== null;

  const column_headings = [
    {label: 'ID', help: 'Harvester id in database'},
    {label: 'Name', help: 'Harvester name'},
    {label: 'Harvester', help: 'Username for harvester database account'},
    {label: 'Is Running', help: 'Displays "True" if harvester is currently running'},
    {label: 'Last Completed Run', help: 'Datetime of last harvester run that successfully ran until completion'},
    {label: 'Periodic Hour', help: 'If set, harvester is run every day on this hour'},
    {label: 'Save', help: 'Click to save edits to a row'},
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
    <TableContainer>
      <Table className={classes.table} size="small">
        <TableHead>
          <TableRow>
            {column_headings.map(heading => (
            <TableCell key={heading.label}>
              <Tooltip title={heading.help}>
                <Typography>
                  {heading.label}
                </Typography>
              </Tooltip>
            </TableCell>
            ))
            }
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
                disableSave={!userIsAdmin}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new harvester">
      <IconButton 
        aria-label="add" 
        onClick={addNewHarvester}
        disabled={!userIsAdmin}
      >
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected harvester">
      <span>
    <IconButton 
      disabled={!userIsAdmin || !isSelected} 
      aria-label="delete" 
      onClick={deleteHarvester}
    >
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    <Tooltip title="Run the selected harvester">
      <span>
      <IconButton 
        disabled={!userIsAdmin || !isSelected || selected.is_running} 
        onClick={runSelectedHarvester}
      >
      <PlayArrowIcon/>
    </IconButton>
    </span>
    </Tooltip>
    </Paper>
    {isSelected &&
      <HarvesterDetail harvester={selected} />
    }
    </Container>
  );
}
