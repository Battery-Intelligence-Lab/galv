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

export type CellFields = {
  url: string;
  id: number;
  name: string;
  form_factor: string;
  link_to_datasheet: string;
  anode_chemistry: string;
  cathode_chemistry: string;
  nominal_capacity: number;
  nominal_cell_weight: number;
  manufacturer: string;
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
    marginLeft: theme.spacing(0),
    flex: 1,
  },
  iconButton: {
    padding: 10,
  },
  paper: {}
}));

const column_headings = [
  // {label: 'ID', help: 'Id in database'},
  {label: 'Name', help: ''},
  {label: 'Form Factor', help: 'Form factor of the cell'},
  {label: 'Datasheet', help: 'Link to the cell\'s datasheet'},
  {label: 'Anode Chemistry', help: 'Chemistry of the cell\'s anode'},
  {label: 'Cathode Chemistry', help: 'Chemistry of the cell\'s cathode'},
  {label: 'Nominal Capacity', help: 'Nominal cell capacity'},
  {label: 'Nominal Weight', help: 'Nominal cell weight'},
  {label: 'Manufacturer', help: 'Manufacturer of the cell'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for cells that are in use'},
  {label: 'Delete', help: 'Delete a cell that is not in use'},
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

export default function Cells() {
  const classes = useStyles();
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const [selected, setSelected] = useState<CellFields|null>(null)

  const get_write_data: (data: CellFields) => Partial<CellFields> = (data) => {
    return {
      name: data.name,
      form_factor: data.form_factor,
      link_to_datasheet: data.link_to_datasheet,
      manufacturer: data.manufacturer,
      anode_chemistry: data.anode_chemistry,
      cathode_chemistry: data.cathode_chemistry,
      nominal_capacity: data.nominal_capacity,
      nominal_cell_weight: data.nominal_cell_weight
    }
  }

  const addNewCell = (data: CellFields) => {
    const insert_data = get_write_data(data)
    Connection.fetch('cells/', {body: JSON.stringify(insert_data), method: 'POST'})
      .then(() => setLastUpdated(new Date()))
  };

  const updateCell = (data: CellFields) => {
    const insert_data = get_write_data(data)
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

  const deleteCell = (data: CellFields) => {
    Connection.fetch(data.url, {method: 'DELETE'})
      .then(() => setLastUpdated(new Date()))
      .then(() => {
        if (selected?.id === data.id)
          setSelected(null)
      })
  };

  function MyTableRow(props: RowFunProps<CellFields>) {
    const classes = useStyles();
    const [row, setRow] = useState<CellFields>({
      url: "",
      id: -1,
      name: "",
      form_factor: "",
      link_to_datasheet: "",
      anode_chemistry: "",
      cathode_chemistry: "",
      nominal_capacity: 0,
      nominal_cell_weight: 0,
      manufacturer: "",
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

    const string_fields: (keyof CellFields)[] = [
      'name', 'manufacturer', 'form_factor', 'link_to_datasheet', 'anode_chemistry', 'cathode_chemistry'
    ]
    const number_fields: (keyof CellFields)[] = ['nominal_capacity', 'nominal_cell_weight']

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
                row.in_use ? row[n] : (<TextField
                  value={row[n]}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  onChange={setValue(n)} />)
              }
            </TableCell>))
          }
          {
            number_fields.map(n => (<TableCell >
              {
                row.in_use ? row[n] : (<TextField
                  value={row[n]}
                  style={{width: 60}}
                  type={"number"}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  onChange={setValue(n)} />)
              }
            </TableCell>))
          }
          <TableCell align="right">
            <Tooltip title="Save changes to cell">
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
            <Tooltip title="Delete cell">
              <span>
                <IconButton
                  disabled={row.in_use}
                  onClick={() => deleteCell(row)}
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
      onRowSave={updateCell}
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
        savedRow={{
          url: "", id: -1, name: "", form_factor: "", link_to_datasheet: "", manufacturer: "",
          anode_chemistry: "", cathode_chemistry: "", nominal_capacity: 0, nominal_cell_weight: 0,
          in_use: false,
        }}
        onRowSave={addNewCell}
        selected={false}
        onSelectRow={() => {}}
        disableSave={false}
        addIcon={true}
      />
    )}
    initial_url={`cells/`}
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
