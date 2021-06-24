import React, { useEffect, useState } from 'react';
import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Paper from '@material-ui/core/Paper';
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
  cells, add_cell, 
  update_cell, delete_cell
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
    fontSize: '10pt',
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

  const rowUnchanged = Object.keys(row).reduce((a, k) => {
    return a && row[k] === savedRow[k];
  }, true);
  console.log('unchanged', rowUnchanged);

  let useRow = row;
  if (useRow.id === undefined) {
    useRow = savedRow;
  }
  Object.keys(useRow).map((k) => {
    useRow[k] = useRow[k] === null ? '' : useRow[k];
  });

  const setValue = (key) => (e) => {
    setRow({...useRow, [key]: e.target.value});
  };

  return (
    <React.Fragment>
    <TableRow 
      onClick={() => {onSelectRow(savedRow);}}
      hover
      selected={selected}
    >
      <TableCell >
        <TextField
          value={useRow.name} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('name')} />
      </TableCell>
      <TableCell align="right">
      <TextField
          value={useRow.manufacturer} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('manufacturer')} />
      </TableCell>
      <TableCell align="right">
        <TextField 
          value={useRow.form_factor} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('form_factor')} />
      </TableCell>
      <TableCell align="right">
        <TextField 
          value={useRow.link_to_datasheet} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('link_to_datasheet')} />
      </TableCell>
      <TableCell align="right">
        <TextField 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          value={useRow.anode_chemistry} 
          onChange={setValue('anode_chemistry')} />
      </TableCell>
      <TableCell align="right">
        <TextField 
          value={useRow.cathode_chemistry} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('cathode_chemistry')} />
      </TableCell>
      <TableCell align="right">
        <TextField 
          value={useRow.nominal_capacity} 
          style={{width: 60}}
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('nominal_capacity')} />
      </TableCell>
    <TableCell align="right">
        <TextField 
          value={useRow.nominal_cell_weight} 
          style={{width: 60}}
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('nominal_cell_weight')} />
      </TableCell>
      <TableCell align="right">
        <Tooltip title="Save changes to cell">
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

export default function Cells() {
  const classes = useStyles();

  const [cellData, setCellData] = useState([])
  const [selected, setSelected] = useState({id: null})
  

  useEffect(() => {
    refreshCells(); 
  }, []);

  const refreshCells = () => {
      cells().then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          setCellData(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
      }
      });
  };

  function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

  const addNewCell = () => {
    add_cell({name: 'Edit me'}).then(refreshCells);
  };
  const deleteCell = () => {
    delete_cell(selected.id).then(refreshCells);
  };
  const updateCell = (value) => {
    Object.keys(value).map((k) => {
      value[k] = value[k] === '' ? null : value[k];
    });
    update_cell(value.id, value).then(refreshCells);
  };

  console.log('cellData', cellData);

const column_headings = [
    {label: 'Name', help: 'Cell Name'},
    {label: 'Manufacturer', help: 'Cell Manufacturer'},
    {label: 'Form Factor', help: 'Form Factor'},
    {label: 'Datasheet', help: 'URL to datasheet'},
    {label: 'Anode Chemistry', help: 'Anode Chemistry'},
    {label: 'Cathode Chemistry', help: 'Cathode Chemistry'},
    {label: 'Nominal Capacity', help: 'Nominal Capacity'},
    {label: 'Save', help: 'Click to save edits to a row'},
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
    <TableContainer>
      <Table className={classes.table} size="small" >
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
          {cellData.map((row) => (
            <MyTableRow 
                key={row.id} 
                savedRow={row} 
                onRowSave={updateCell} 
                selected={selected.id === row.id}
                onSelectRow={setSelected}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new cell">
      <IconButton aria-label="add" onClick={addNewCell}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected cell">
      <span>
    <IconButton disabled={selected.id === null} aria-label="delete" onClick={deleteCell}>
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    </Paper>
    </Container>
  );
}
