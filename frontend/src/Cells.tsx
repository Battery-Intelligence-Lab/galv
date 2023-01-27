import React, { Fragment } from 'react';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import DeleteIcon from '@mui/icons-material/Delete';
import Connection from "./APIConnection";
import AsyncTable from "./AsyncTable";

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

const columns = [
  // {label: 'ID', help: 'Id in database'},
  {label: 'Name', help: ''},
  {label: 'Manufacturer', help: 'Manufacturer of the cell'},
  {label: 'Form Factor', help: 'Form factor of the cell'},
  {label: 'Datasheet', help: 'Link to the cell\'s datasheet'},
  {label: 'Anode Chemistry', help: 'Chemistry of the cell\'s anode'},
  {label: 'Cathode Chemistry', help: 'Chemistry of the cell\'s cathode'},
  {label: 'Nominal Capacity', help: 'Nominal cell capacity'},
  {label: 'Nominal Weight', help: 'Nominal cell weight'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for cells that are in use'},
  {label: 'Delete', help: 'Delete a cell that is not in use'},
]

const string_fields = [
  'name', 'manufacturer', 'form_factor', 'link_to_datasheet', 'anode_chemistry', 'cathode_chemistry'
] as const
const number_fields = ['nominal_capacity', 'nominal_cell_weight'] as const

export default function Cells() {
  const classes = useStyles();

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
    return Connection.fetch('cells/', {body: JSON.stringify(insert_data), method: 'POST'})
  };

  const updateCell = (data: CellFields) => {
    const insert_data = get_write_data(data)
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const deleteCell = (data: CellFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<CellFields>
          columns={columns}
          row_generator={(cell, context) => [
            ...string_fields.map(n => <Fragment>
              <TextField
                name={n}
                value={cell[n]}
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                onChange={context.update}
              />
            </Fragment>),
            ...number_fields.map(n => <Fragment>
              <TextField
                name={n}
                style={{width: 60}}
                type={"number"}
                value={cell[n]}
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                onChange={context.update}
              />
            </Fragment>),
            <Fragment>
              <Tooltip title="Save changes to cell">
              <span>
                <IconButton
                  disabled={!context.value_changed || cell.in_use}
                  onClick={
                  context.is_new_row?
                    () => addNewCell(cell).then(context.refresh_all_rows) :
                    () => updateCell(cell).then(context.refresh)}
                >
                  {context.is_new_row? <AddIcon/> : <SaveIcon/>}
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>,
            context.is_new_row? <Fragment key="delete"/> : <Fragment>
              <Tooltip title="Delete cell">
              <span>
                <IconButton
                  disabled={cell.in_use}
                  onClick={() => deleteCell(cell).then(context.refresh)}
                >
                  <DeleteIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>
          ]}
          new_row_values={{
            name: '', manufacturer: '', form_factor: '', link_to_datasheet: '', anode_chemistry: '', cathode_chemistry: '',
            nominal_capacity: 0, nominal_cell_weight: 0
          }}
          initial_url="cells/?all=true"
        />
      </Paper>
    </Container>
  );
}
