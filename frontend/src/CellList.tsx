import React, {Fragment} from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import Connection from "./APIConnection";
import AsyncTable, {RowGeneratorContext} from "./AsyncTable";
import Typography from "@mui/material/Typography";
import {CellFamilyFields} from "./Cells";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";

export type CellFields = {
  id: number;
  url: string;
  uid: string;
  display_name: string;
  family: string;
  datasets: string[];
  in_use: boolean;
}
type CellDetailProps = {
  family: CellFamilyFields,
  [key: string]: any
}

const columns = [
  {label: 'UID', help: 'Unique identifier for the cell. This should be a serial number or similar unique to the specific cell.'},
  {label: 'Display Name', help: 'Human-friendly name for the cell'},
  {label: 'Linked Datasets', help: 'Number of datasets linked to this cell'},
  {label: 'Actions', help: 'Save / Delete a cell. Edits are disabled for cells that are in use'}
]

export default function CellList(props: CellDetailProps) {
  const classes = useStyles();

  const addNewCell = (data: CellFields, context: RowGeneratorContext<CellFields>) => {
    context.mark_loading(true)
    const insert_data: Partial<CellFields> = {uid: data.uid, family: props.family.url}
    if (data.display_name)
      insert_data.display_name = data.display_name
    return Connection.fetch('cells/', {body: JSON.stringify(insert_data), method: 'POST'})
  };

  const updateCell = (data: CellFields, context: RowGeneratorContext<CellFields>) => {
    context.mark_loading(true)
    const insert_data = {uid: data.uid, display_name: data.display_name, family: props.family.url}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(r => r.content)
  };

  const deleteCell = (data: CellFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<CellFields>
          classes={classes}
          columns={columns}
          row_generator={(cell, context) =>
            cell.family !== props.family.url ? null : [
            <Fragment>
              <TextField
                name="uid"
                value={cell.uid}
                disabled={cell.in_use}
                placeholder={`Serial number or other unique identifer`}
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                onChange={context.update}
              />
            </Fragment>,
            <Fragment>
              <TextField
                name="display_name"
                value={cell.display_name}
                disabled={cell.in_use}
                placeholder={`${props.family.name}_#`}
                InputProps={{
                  classes: {
                    input: classes.resize,
                  },
                }}
                onChange={context.update}
              />
            </Fragment>,
            context.is_new_row? <Fragment key="datasets" /> : <Fragment>
              {cell.datasets.length}
            </Fragment>,
            <Fragment key="actions">
              <ActionButtons
                classes={classes}
                onSave={
                  context.is_new_row?
                    () => addNewCell(cell, context).then(() => context.refresh_all_rows()) :
                    () => updateCell(cell, context).then(context.refresh)
                }
                saveButtonProps={{disabled: !context.value_changed || cell.in_use}}
                saveIconProps={{component: context.is_new_row? AddIcon : SaveIcon}}
                onDelete={
                  () =>
                    window.confirm(`Delete cell ${cell.display_name}?`) &&
                    deleteCell(cell).then(context.refresh)
                }
                deleteButtonProps={{disabled: context.is_new_row || cell.in_use}}
              />
            </Fragment>
          ]}
          new_row_values={{uid: '', display_name: '', family: props.family.url, datasets: []}}
          url={`cells/`}
        />
        <Typography p={2} fontSize="small">
          Note: Cells assigned to existing datasets cannot be changed.
        </Typography>
      </Paper>
    </Container>
  );
}
