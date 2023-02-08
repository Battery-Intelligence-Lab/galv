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
import {CellFamilyFields} from "./Cells";

export type CellFields = {
  id: number;
  url: string;
  display_name: string;
  family: string;
  datasets: string[];
}
type CellDetailProps = {
  family: CellFamilyFields,
  [key: string]: any
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
  {label: 'Display Name', help: 'Human-friendly name for the cell'},
  {label: 'Linked Datasets', help: 'Number of datasets linked to this cell'},
  {label: 'Save', help: 'Click to save edits to a row. Edits are disabled for cells that are in use'},
  {label: 'Delete', help: 'Delete a cell that is not in use'},
]

export default function CellList(props: CellDetailProps) {
  const classes = useStyles();

  const addNewCell = (data: CellFields, context: RowGeneratorContext<CellFields>) => {
    context.mark_loading(true)
    const insert_data = {display_name: data.display_name, family: props.family.url}
    return Connection.fetch('cells/', {body: JSON.stringify(insert_data), method: 'POST'})
  };

  const updateCell = (data: CellFields, context: RowGeneratorContext<CellFields>) => {
    context.mark_loading(true)
    const insert_data = {display_name: data.display_name, family: props.family.url}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  };

  const deleteCell = (data: CellFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<CellFields>
          columns={columns}
          row_generator={(cell, context) => [
            <Fragment>
              <TextField
                name="display_name"
                value={cell.display_name}
                disabled={cell.datasets.length > 0}
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
            cell.datasets.length > 0? <Fragment key="save"/> : <Fragment>
              <Tooltip title={
                cell.datasets.length > 0? "Cannot update a cell that is used by datasets." :
                  context.is_new_row? "Add cell" : "Save changes to cell"
              }>
              <span>
                <IconButton
                  disabled={cell.datasets.length > 0}
                  onClick={
                    context.is_new_row?
                      () => addNewCell(cell, context).then(context.refresh_all_rows) :
                      () => updateCell(cell, context).then(context.refresh)}
                >
                  {context.is_new_row? <AddIcon/> : <SaveIcon/>}
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>,
            context.is_new_row || cell.datasets.length > 0? <Fragment key="delete"/> : <Fragment>
              <Tooltip title="Delete cell">
              <span>
                <IconButton onClick={() => deleteCell(cell).then(context.refresh)}>
                  <DeleteIcon />
                </IconButton>
              </span>
              </Tooltip>
            </Fragment>
          ]}
          new_row_values={{display_name: '', datasets: []}}
          url={`cells/?all=true&family__id=${props.family.id}`}
          fetch_depth={0}
        />
        <Typography p={2} fontSize="small">
          Note: Cells assigned to existing datasets cannot be changed.
        </Typography>
      </Paper>
    </Container>
  );
}
