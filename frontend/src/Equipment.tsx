import React, { Fragment } from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import AsyncTable from './AsyncTable';
import Connection from "./APIConnection";
import ActionButtons from "./ActionButtons";
import useStyles from "./UseStyles";

export type EquipmentFields = {
  url: string;
  id: number;
  name: string;
  type: string;
  in_use: boolean;
}

const columns = [
  {label: 'Name', help: 'Equipment Name'},
  {label: 'Type', help: 'Equipment Type'},
  {label: 'Save', help: 'Save / Delete equipment. Edits are disabled for equipment that is in use'},
]

const string_fields = ['name', 'type'] as const

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
      .then(r => r.content)
  };

  const deleteEquipment = (data: EquipmentFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<EquipmentFields>
          classes={classes}
          columns={columns}
          row_generator={(equipment, context) => [
            ...string_fields.map(n => <Fragment>
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
            <Fragment key="actions">
              <ActionButtons
                classes={classes}
                onSave={
                  context.is_new_row?
                    () => addNewEquipment(equipment).then(context.refresh_all_rows) :
                    () => updateEquipment(equipment).then(context.refresh)
                }
                saveButtonProps={{disabled: !context.value_changed || equipment.in_use}}
                saveIconProps={{component: context.is_new_row? AddIcon : SaveIcon}}
                onDelete={
                  () =>
                    window.confirm(`Delete equipment ${equipment.name}?`) &&
                    deleteEquipment(equipment).then(context.refresh)
                }
                deleteButtonProps={{disabled: context.is_new_row || equipment.in_use}}
              />
            </Fragment>
          ]}
          new_row_values={{name: '', type: ''}}
          url={`equipment/`}
          styles={classes}
        />
      </Paper>
    </Container>
  );
}
