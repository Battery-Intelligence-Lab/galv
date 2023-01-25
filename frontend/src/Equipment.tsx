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
import AsyncTable, {CellContext} from './AsyncTable';
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

const columns = [
  {label: 'Name', help: 'Equipment Name'},
  {label: 'Type', help: 'Equipment Type'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for equipment that is in use'},
  {label: 'Delete', help: 'Delete equipment that is not in use'},
]

const string_fields: (keyof EquipmentFields)[] = ['name', 'type']

export default function Equipment() {
  const classes = useStyles();

  const get_write_data: (data: EquipmentFields) => Partial<EquipmentFields> = (data) => {
    return { name: data.name, type: data.type }
  }

  const addNewEquipment = (data: EquipmentFields) => {
    const insert_data = get_write_data(data)
    return Connection.fetch('equipment/', {body: JSON.stringify(insert_data), method: 'POST'})
  };

  const updateEquipment = (data: EquipmentFields) => {
    const insert_data = get_write_data(data)
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const deleteEquipment = (data: EquipmentFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable
          columns={columns}
          rows={[
            ...string_fields.map(n => (equipment: EquipmentFields, context: CellContext) => <Fragment>
              {
                equipment.in_use ? equipment[n] : <TextField
                  name={n}
                  value={equipment[n]}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  onChange={context.update}
                />
              }
            </Fragment>),
            (equipment, context) => <Fragment>
              <Tooltip title="Save changes to equipment">
              <span>
                <IconButton
                  disabled={!equipment._changed || equipment.in_use}
                  onClick={() => updateEquipment(equipment).then(context.refresh)}
                >
                  <SaveIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>,
            (equipment, context) => <Fragment>
              <Tooltip title="Delete equipment">
              <span>
                <IconButton
                  disabled={equipment.in_use}
                  onClick={() => deleteEquipment(equipment).then(context.refresh)}
                >
                  <DeleteIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>
          ]}
          new_entry_row={[
            ...string_fields.map(n => (equipment: EquipmentFields, context: CellContext) => <Fragment>
              {
                equipment.in_use ? equipment[n] : <TextField
                  name={n}
                  value={equipment[n]}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  onChange={context.update}
                />
              }
            </Fragment>),
            (equipment, context) => <Fragment>
              <Tooltip title="Save changes to equipment">
              <span>
                <IconButton
                  disabled={!equipment._changed}
                  onClick={() => addNewEquipment(equipment).then(context.refresh_all_rows)}
                >
                  <AddIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>,
            <Fragment key="delete"/>
          ]}
          new_row_values={{name: '', type: ''}}
          initial_url={`equipment/?all=true`}
          styles={classes}
        />
      </Paper>
    </Container>
  );
}
