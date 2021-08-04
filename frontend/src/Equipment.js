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
