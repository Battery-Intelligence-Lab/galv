import React, { useEffect, useState } from 'react';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import Paper from '@mui/material/Paper';
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
import { 
  equipment, add_equipment, 
  update_equipment, delete_equipment
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

  let useRow = row;
  if (useRow.id === undefined) {
    useRow = savedRow;
  }
  Object.keys(useRow).map((k) => {
    useRow[k] = useRow[k] === null ? '' : useRow[k];
    return null
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
      <TableCell>
      <TextField
          value={useRow.type} 
          InputProps={{
            classes: {
              input: classes.resize,
            },
          }}
          onChange={setValue('type')} />
      </TableCell>
      <TableCell>
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

export default function Equipment() {
  const classes = useStyles();

  const [equipData, setEquipData] = useState([])
  const [selected, setSelected] = useState({id: null})
  

  useEffect(() => {
    refreshEquip(); 
  }, []);

  const refreshEquip = () => {
      equipment().then((response) => {
      if (response.ok) {
        return response.json().then((result) => {
          setEquipData(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
      }
      });
  };

  const addNewEquip = () => {
    add_equipment({name: 'Edit me'}).then(refreshEquip);
  };
  const deleteEquip = () => {
    delete_equipment(selected.id).then(refreshEquip);
  };
  const updateEquip = (value) => {
    Object.keys(value).map((k) => {
      value[k] = value[k] === '' ? null : value[k];
      return null
    });
    update_equipment(value.id, value).then(refreshEquip);
  };

  const column_headings = [
    {label: 'Name', help: 'Equipment Name'},
    {label: 'Type', help: 'Equipment Type'},
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
          {equipData.map((row) => (
            <MyTableRow 
                key={row.id} 
                savedRow={row} 
                onRowSave={updateEquip} 
                selected={selected.id === row.id}
                onSelectRow={setSelected}
            />
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    <Tooltip title="Add new equipment">
      <IconButton aria-label="add" onClick={addNewEquip}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected equipment">
      <span>
    <IconButton disabled={selected.id === null} aria-label="delete" onClick={deleteEquip}>
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    </Paper>
    </Container>
  );
}
