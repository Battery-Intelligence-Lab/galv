// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React, {Fragment, useState} from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import Connection from "./APIConnection";
import AsyncTable, {RowGeneratorContext} from "./AsyncTable";
import Typography from "@mui/material/Typography";
import CellList, {CellFields} from "./CellList";
import Stack from "@mui/material/Stack";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";

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
  in_use: boolean;
}

const columns = [
  {label: 'Source', help: ''},
  {label: 'Type', help: ''},
  {label: 'Chemistry', help: ''},
  {label: 'Statistics', help: 'Nominal values for cell'},
  {label: 'Actions', help: 'View Cells / Save / Delete cell families'},
]

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
      .then(r => r.content)
  };

  const deleteCell = (data: CellFamilyFields) => Connection.fetch(data.url, {method: 'DELETE'})

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<CellFamilyFields>
          classes={classes}
          columns={columns}
          row_generator={(family, context) => [
            <Fragment>
              <Stack spacing={1}>
                <Tooltip title="Name for this Cell Family" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="name"
                    label="Name"
                    fullWidth
                    value={family.name}
                    onChange={context.update}
                  />
                </Tooltip>
                <Tooltip title="Manufacturer name" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="manufacturer"
                    label="Manufacturer"
                    fullWidth
                    value={family.manufacturer}
                    onChange={context.update}
                  />
                </Tooltip>
              </Stack>
            </Fragment>,
            <Fragment>
              <Stack spacing={1}>
                <Tooltip title="Form Factor name" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="form_factor"
                    label="Form Factor"
                    fullWidth
                    value={family.form_factor}
                    onChange={context.update}
                  />
                </Tooltip>
                <Tooltip title="Datasheet link" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="link_to_datasheet"
                    label="Datasheet"
                    fullWidth
                    value={family.link_to_datasheet}
                    onChange={context.update}
                  />
                </Tooltip>
              </Stack>
            </Fragment>,
            <Fragment>
              <Stack spacing={1}>
                <Tooltip title="Anode Chemistry type" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="anode_chemistry"
                    label="Anode"
                    fullWidth
                    value={family.anode_chemistry}
                    onChange={context.update}
                  />
                </Tooltip>
                <Tooltip title="Cathode Chemistry type" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="cathode_chemistry"
                    label="Cathode"
                    fullWidth
                    value={family.cathode_chemistry}
                    onChange={context.update}
                  />
                </Tooltip>
              </Stack>
            </Fragment>,
            <Fragment>
              <Stack spacing={1}>
                <Tooltip title="Nominal value" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="nominal_capacity"
                    label="Capacity"
                    fullWidth
                    type={"number"}
                    value={family.nominal_capacity}
                    onChange={context.update}
                  />
                </Tooltip>
                <Tooltip title="Nominal value" placement="right">
                  <TextField
                    InputProps={{classes: {input: classes.resize}}}
                    name="nominal_cell_weight"
                    label="Weight"
                    fullWidth
                    type={"number"}
                    value={family.nominal_cell_weight}
                    onChange={context.update}
                  />
                </Tooltip>
              </Stack>
            </Fragment>,
            <Fragment key="actions">
              <ActionButtons
                classes={classes}
                onInspect={() => selected?.id === family.id? setSelected(null) : setSelected(family)}
                inspectButtonProps={{disabled: context.is_new_row}}
                inspectIconProps={selected?.id === family.id ? {color: 'info'} : {}}
                onSave={
                  context.is_new_row?
                    () => addNewCell(family, context).then(() => context.refresh_all_rows()) :
                    () => updateCell(family, context).then(context.refresh)
                }
                saveButtonProps={{disabled: !context.value_changed || family.in_use}}
                saveIconProps={{component: context.is_new_row? AddIcon : SaveIcon}}
                onDelete={
                  () =>
                    window.confirm(`Delete cell family ${family.name}?`) &&
                    deleteCell(family).then(context.refresh)
                }
                deleteButtonProps={{disabled: context.is_new_row || family.in_use}}
              />
            </Fragment>
          ]}
          new_row_values={{
            name: '', manufacturer: '', form_factor: '', link_to_datasheet: '', anode_chemistry: '', cathode_chemistry: '',
            nominal_capacity: 0, nominal_cell_weight: 0, cells: []
          }}
          url="cell_families/"
        />
        <Typography p={2} fontSize="small">
          Note: Cell families with cells cannot be changed.
        </Typography>
      </Paper>
      {selected !== null && <CellList family={selected} />}
    </Container>
  );
}
