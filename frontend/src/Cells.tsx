import React, {Fragment, useState} from 'react';
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
import AsyncTable, {RowGeneratorContext} from "./AsyncTable";
import Typography from "@mui/material/Typography";
import SearchIcon from "@mui/icons-material/Search";
import CellList, {CellFields} from "./CellList";

export type CellFamilyFields = {
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
  cells: CellFields[];
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
  {label: 'Name', help: ''},
  {label: 'Manufacturer', help: 'Manufacturer of the cell family'},
  {label: 'Form Factor', help: 'Form factor of the cell family'},
  {label: 'Datasheet', help: 'Link to the cell family\'s datasheet'},
  {label: 'Anode Chemistry', help: 'Chemistry of the cell family\'s anode'},
  {label: 'Cathode Chemistry', help: 'Chemistry of the cell family\'s cathode'},
  {label: 'Nominal Capacity', help: 'Nominal cell family capacity'},
  {label: 'Nominal Weight', help: 'Nominal cell family weight'},
  {label: 'Details', help: 'View cells in this family'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for cell families that are in use'},
  {label: 'Delete', help: 'Delete a cell family that is not in use'},
]

const string_fields = [
  'name', 'manufacturer', 'form_factor', 'link_to_datasheet', 'anode_chemistry', 'cathode_chemistry'
] as const
const number_fields = ['nominal_capacity', 'nominal_cell_weight'] as const

export default function Cells() {
  const classes = useStyles();
  const [selected, setSelected] = useState<CellFamilyFields|null>(null)

  const get_write_data: (data: CellFamilyFields) => Partial<CellFamilyFields> = (data) => {
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

  const addNewCell = (data: CellFamilyFields, context: RowGeneratorContext<CellFamilyFields>) => {
    context.mark_loading(true)
    const insert_data = get_write_data(data)
    return Connection.fetch('cell_families/', {body: JSON.stringify(insert_data), method: 'POST'})
  };

  const updateCell = (data: CellFamilyFields, context: RowGeneratorContext<CellFamilyFields>) => {
    context.mark_loading(true)
    const insert_data = get_write_data(data)
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const deleteCell = (data: CellFamilyFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<CellFamilyFields>
          columns={columns}
          row_generator={(family, context) => [
            ...string_fields.map(n => <Fragment>
              <TextField
                name={n}
                value={family[n]}
                disabled={family.cells.length > 0}
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
                value={family[n]}
                disabled={family.cells.length > 0}
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                onChange={context.update}
              />
            </Fragment>),
            context.is_new_row? <Fragment key="select"/> : <Fragment key="select">
              <IconButton onClick={() => selected?.id === family.id? setSelected(null) : setSelected(family)}>
                <SearchIcon color={selected?.id === family.id? 'info' : undefined} />
              </IconButton>
            </Fragment>,
            family.cells.length > 0? <Fragment key="save"/> : <Fragment>
              <Tooltip title={
                family.cells.length > 0? "Cannot update a cell family that is used by cells." :
                  context.is_new_row? "Add cell family" : "Save changes to cell family"
              }>
              <span>
                <IconButton
                  disabled={!context.value_changed || family.cells.length > 0}
                  onClick={
                    context.is_new_row?
                      () => addNewCell(family, context).then(context.refresh_all_rows) :
                      () => updateCell(family, context).then(context.refresh)}
                >
                  {context.is_new_row? <AddIcon/> : <SaveIcon/>}
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>,
            context.is_new_row || family.cells.length > 0? <Fragment key="delete"/> : <Fragment>
              <Tooltip title="Delete cell family">
              <span>
                <IconButton onClick={() => deleteCell(family).then(context.refresh)}>
                  <DeleteIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>
          ]}
          new_row_values={{
            name: '', manufacturer: '', form_factor: '', link_to_datasheet: '', anode_chemistry: '', cathode_chemistry: '',
            nominal_capacity: 0, nominal_cell_weight: 0, cells: []
          }}
          url="cell_families/?all=true"
          fetch_depth={0}
        />
        <Typography p={2} fontSize="small">
          Note: Cell families with cells cannot be changed.
        </Typography>
      </Paper>
      {selected !== null && <CellList family={selected} />}
    </Container>
  );
}
