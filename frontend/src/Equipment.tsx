import React, { useEffect, useState } from 'react';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import PaginatedTable, {RowFunProps} from './PaginatedTable';
import Connection from "./APIConnection";

export type EquipmentFields = {
  url: string;
  id: number;
  name: string;
  type: string;
  in_use: boolean;
}

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
  paper: {}
}));

const column_headings = [
  {label: 'Name', help: 'Equipment Name'},
  {label: 'Type', help: 'Equipment Type'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for equipment that is in use'},
  {label: 'Delete', help: 'Delete equipment that is not in use'},
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

export default function Equipment() {
  const classes = useStyles();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const [selected, setSelected] = useState<EquipmentFields|null>(null)

  const get_write_data: (data: EquipmentFields) => Partial<EquipmentFields> = (data) => {
    return { name: data.name, type: data.type }
  }

  const addNewEquipment = (data: EquipmentFields) => {
    const insert_data = get_write_data(data)
    Connection.fetch('equipment/', {body: JSON.stringify(insert_data), method: 'POST'})
      .then(() => setLastUpdated(new Date()))
  };

  const updateEquipment = (data: EquipmentFields) => {
    const insert_data = get_write_data(data)
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

  const deleteEquipment = (data: EquipmentFields) => {
    Connection.fetch(data.url, {method: 'DELETE'})
      .then(() => setLastUpdated(new Date()))
      .then(() => {
        if (selected?.id === data.id)
          setSelected(null)
      })
  };

  function MyTableRow(props: RowFunProps<EquipmentFields>) {
    const classes = useStyles();
    const [row, setRow] = useState<EquipmentFields>({
      url: "",
      id: -1,
      name: "",
      type: "",
      in_use: false,
    })
    const [dirty, setDirty] = useState<boolean>(false)

    useEffect(() => {
      if (!dirty && props.savedRow) {
        setRow(props.savedRow);
      }
    }, [dirty, props.savedRow]);

    let useRow = row;
    if (row.id === -1 && props.savedRow)
      useRow = props.savedRow;

    const setValue = (key: string) => (e: any) => {
      setDirty(true);
      setRow({...useRow, [key]: e.target?.value});
    };

    const Icon = props.addIcon ? <AddIcon/> : <SaveIcon/> ;

    const string_fields: (keyof EquipmentFields)[] = ['name', 'type']

    return (
      <React.Fragment>
        <TableRow
          onClick={() => {props.onSelectRow(props.savedRow);}}
          hover
          selected={props.selected}
        >
          {
            string_fields.map(n => (<TableCell >
              {
                row.in_use ? row[n] : <TextField
                  value={row[n]}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  onChange={setValue(n)}
                />
              }
            </TableCell>))
          }
          <TableCell align="right">
            <Tooltip title="Save changes to equipment">
              <span>
                <IconButton
                  disabled={!dirty || row.in_use}
                  onClick={() => {props.onRowSave(row);}}
                >
                  {Icon}
                </IconButton>
              </span>
            </Tooltip>
          </TableCell>
          <TableCell align="right">
            <Tooltip title="Delete equipment">
              <span>
                <IconButton
                  disabled={row.in_use}
                  onClick={() => deleteEquipment(useRow)}
                >
                  <DeleteIcon />
                </IconButton>
              </span>
            </Tooltip>
          </TableCell>
        </TableRow>
      </React.Fragment>
    )
  }

  function table_row_generator(row: any) {
    return (<MyTableRow
      key={row.id}
      savedRow={row}
      onRowSave={updateEquipment}
      selected={selected !== null && selected.id === row.id}
      onSelectRow={setSelected}
    />)
  }

  const paginated_table = (<PaginatedTable
    header={(<TableHead>{table_head}</TableHead>)}
    row_fun= {table_row_generator}
    new_entry_row={(
      <MyTableRow
        key={"new_cell"}
        savedRow={{url: "", id: -1, name: "", type: "", in_use: false}}
        onRowSave={addNewEquipment}
        selected={false}
        onSelectRow={() => {}}
        disableSave={false}
        addIcon={true}
      />
    )}
    initial_url={`equipment/`}
    styles={classes}
    last_updated={lastUpdated}
  />)

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        {paginated_table}
      </Paper>
    </Container>
  );
}
