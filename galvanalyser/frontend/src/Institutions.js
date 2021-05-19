import React, { useEffect, useState } from 'react';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Paper from '@material-ui/core/Paper';
import InputBase from '@material-ui/core/InputBase';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import IconButton from '@material-ui/core/IconButton';
import TableCell from '@material-ui/core/TableCell';
import Container from '@material-ui/core/Container';
import SaveIcon from '@material-ui/icons/Save';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import DeleteIcon from '@material-ui/icons/Delete';
import TableRow from '@material-ui/core/TableRow';
import { 
  institutions, add_institution, 
  update_institution, delete_institution
} from './Api'

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  table: {
    minWidth: 650,
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

  const rowUnchanged = row.name === savedRow.name;
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
          value={useRow.name}
          onChange={(e) => {
            setRow({...row, name: e.target.value});
          }} 
        >
        </TextField>
      </TableCell>

      <TableCell align="right">
        <Tooltip title="Save changes to institution">
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

export default function Institution() {
  const classes = useStyles();

  const [institutionData, setInstitutionData] = useState([])
  const [selected, setSelected] = useState({id: null})

  useEffect(() => {
    refreshInstitutions(); 
  }, []);

  const refreshInstitutions = () => {
      institutions().then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          setInstitutionData(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
      }
      });
  };

  const addNewInstitution= () => {
    add_institution({name: 'Edit Me'}).then(refreshInstitutions);
  };
  const deleteInstition= () => {
    delete_institution(selected.id).then(refreshInstitutions);
  };
  const updateInstitution = (value) => {
    update_institution(value.id, value).then(refreshInstitutions);
  };

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
    <TableContainer>
      <Table className={classes.table} size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell align="right">Name</TableCell>
            <TableCell align="right">Save</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {institutionData.map((row) => (
            <MyTableRow 
                key={row.id} 
                savedRow={row} 
                onRowSave={updateInstitution} 
                selected={selected.id === row.id}
                onSelectRow={setSelected}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new institution">
      <IconButton aria-label="add" onClick={addNewInstitution}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected institution">
      <span>
    <IconButton disabled={selected.id === null} aria-label="delete" onClick={deleteInstition}>
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    </Paper>
    </Container>
  );
}
