// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState, Fragment, ReactElement, useEffect} from "react";
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import { useNavigate } from "react-router-dom";
import GetDatasetPython from "./GetDatasetPython"
import GetDatasetMatlab from "./GetDatasetMatlab"
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Connection from "./APIConnection"
import AsyncTable, {RowGeneratorContext} from "./AsyncTable"
import Paper from "@mui/material/Paper";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import {UserSet} from "./UserRoleSet";
import {CellFields} from "./CellList";
import MenuItem from "@mui/material/MenuItem";
import {EquipmentFields} from "./Equipment";
import OutlinedInput from "@mui/material/OutlinedInput";
import Box from "@mui/material/Box";
import ListItem from "@mui/material/ListItem";
import Tooltip from "@mui/material/Tooltip";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";
import Stack from "@mui/material/Stack";
import DatasetChart from "./DatasetChart";

export type DatasetFields = {
  url: string;
  id: number;
  file: string;
  name: string;
  type: string;
  date: string;
  cell: string | null;
  equipment: string[];
  columns: string[];
  purpose: string;
  user_sets: UserSet[];
}

export default function Datasets() {
  const { classes } = useStyles();
  const [selected, setSelected] = useState<DatasetFields|null>(null)

  useEffect(() => {
    console.log(`Dataset useEffect`)
    Connection.fetchMany<DatasetFields>('datasets/').catch(e => console.warn)
    Connection.fetchMany<CellFields>('cells/').catch(e => console.warn)
    Connection.fetchMany<EquipmentFields>('equipment/').catch(e => console.warn)
  }, [Connection.user])

  const updateRow = (data: DatasetFields, context: RowGeneratorContext<DatasetFields>) => {
    context.mark_loading(true)
    const insert_data: any = {
      name: data.name,
      type: data.type,
      cell: data.cell || null,
      equipment: data.equipment
    }
    if (data.purpose) insert_data.purpose = data.purpose
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(r => r.content)
  }

  const columns = [
    {label: 'Date', help: 'Date of Test'},
    {label: 'Properties', help: ''},
    {label: 'Equipment', help: 'Equipment used to generate the dataset'},
    {label: 'Actions', help: 'Inspect / Save dataset'}
  ]

  const [codeOpen, setCodeOpen] = React.useState(false);

  const handleCodeOpen = () => {
    setCodeOpen(true);
  };

  const handleCodeClose = () => {
    setCodeOpen(false);
  };

  const [codeMatlabOpen, setMatlabCodeOpen] = React.useState(false);

  const handleMatlabCodeOpen = () => {
    setMatlabCodeOpen(true);
  };

  const handleMatlabCodeClose = () => {
    setMatlabCodeOpen(false);
  };

  const get_cell_items = (dataset: DatasetFields) => {
    const cellList = Connection.results.get_contents<CellFields>('cells/')
    const menuItem = (cell: CellFields) => <MenuItem key={cell.id} value={cell.url}>{cell.uid}{cell.display_name? ` (${cell.display_name})` : ''}</MenuItem>
    const items: ReactElement[] = []
    if (dataset?.cell) {
      const cell = cellList.find(c => c.url === dataset.cell)
      if (cell !== undefined)
        items.push(menuItem(cell))
    }
    items.push(<MenuItem key="na" value=""><em>None</em></MenuItem>)
    if (cellList.length)
      items.push(...cellList.filter(c => c.url !== dataset.cell).map(menuItem))
    if (!items.length)
      items.push(<MenuItem key="empty" disabled={true}><em>No cells defined</em></MenuItem>)
    return items
  }

  const get_equipment_items = (dataset: DatasetFields) => {
    const equipmentList = Connection.results.get_contents<EquipmentFields>('equipment/')
    const menuItem = (equipment: EquipmentFields) =>
      <MenuItem key={equipment.id} value={equipment.url}>{equipment.name}</MenuItem>
    const items: ReactElement[] = []
    if (dataset?.equipment) {
      dataset.equipment.map(e => equipmentList.find(eq => eq.url === e))
        .forEach(e => {
          if (e !== undefined)
            items.push(menuItem(e))
        })
    }
    if (equipmentList.length)
      items.push(...equipmentList.filter(e => !dataset?.equipment.includes(e.url)).map(menuItem))
    if (!items.length)
      items.push(<MenuItem key="empty" disabled={true}><em>No equipment defined</em></MenuItem>)
    return items
  }

  const purposeOptions = [
    'Ageing',
    'Real world/drive cycling',
    'Characterisation/check-up',
    'Thermal performance',
    'Pulse',
    'Charge',
    'Discharge',
    'EIS',
    'GITT',
    'Pseudo-OCV',
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<DatasetFields>
          classes={classes}
          columns={columns}
          row_generator={(dataset, context) => [
            <Fragment>
              {
                Intl.DateTimeFormat(
                  'en-GB',
                  {dateStyle: 'short'})
                  .format(Date.parse(dataset.date))
              }
            </Fragment>,
            <Fragment>
              <Box>
                <Grid container spacing={1}>
                  <Grid item>
                    <Tooltip title="File from which dataset was extracted" placement="right">
                      <TextField
                        InputProps={{classes: {input: classes.resize}}}
                        name="name"
                        label="Name"
                        fullWidth
                        value={dataset.name}
                        onChange={context.update}
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <FormControl fullWidth>
                      <InputLabel key='label' id={`purpose-select-label-${dataset.id}`}>Purpose</InputLabel>
                      <Select
                        key='select'
                        id={`purpose-select-${dataset.id}`}
                        name="purpose"
                        value={dataset.purpose || ''}
                        sx={{minWidth: 100}}
                        onChange={(e) => context.update_direct('purpose', e.target.value)}
                      >
                        <MenuItem key="none" value=""><em>None</em></MenuItem>
                        {purposeOptions.map(p => <MenuItem key={p} value={p}>{p}</MenuItem>)}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
                <Grid container spacing={1} pt={1}>
                  <Grid item>
                    <Tooltip title="Type of parser used to process the file" placement="right">
                      <TextField
                        InputProps={{classes: {input: classes.resize}}}
                        name="type"
                        label="Type"
                        fullWidth
                        value={dataset.type}
                        onChange={context.update}
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <FormControl fullWidth>
                      <InputLabel key='label' id={`cell-select-label-${dataset.id}`}>Cell</InputLabel>
                      <Select
                        key='select'
                        id={`cell-select-${dataset.id}`}
                        name="cell"
                        value={dataset.cell || ''}
                        sx={{minWidth: 100}}
                        onChange={
                          (e) => context.update_direct('cell', e.target.value || null)
                        }
                      >
                        {get_cell_items(dataset)}
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </Box>
            </Fragment>,
            <Fragment>
              <Select
                id={`equipment-select-${dataset.id}`}
                input={<OutlinedInput id="select-multiple-chip" label="Chip" />}
                renderValue={(selected) => (
                  <Stack spacing={0.5}>
                    {selected.map((value) => (
                      <ListItem key={value}>
                        {Connection.results.get_contents<EquipmentFields>(value)[0]?.name || '???'}
                      </ListItem>
                    ))}
                  </Stack>
                )}
                name={'equipment'}
                sx={{minWidth: 100}}
                multiple
                value={dataset?.equipment}
                onChange={
                  (e) => {
                    const value: string[] = typeof e.target.value === 'string' ?
                      [e.target.value] : e.target.value
                    context.update_direct('equipment', value)
                  }
                }
              >
                {get_equipment_items(dataset)}
              </Select>
            </Fragment>,
            <Fragment key="actions">
              <ActionButtons
                classes={classes}
                onInspect={() => selected?.id === dataset.id? setSelected(null) : setSelected(dataset)}
                inspectIconProps={selected?.id === dataset.id ? {color: 'info'} : {}}
                onSave={() => updateRow(dataset, context).then(context.refresh)}
                saveButtonProps={{disabled: !context.value_changed}}
              />
            </Fragment>
          ]}
          subrow={
            <Stack spacing={1} justifyContent="center" alignItems="center">
              <Stack spacing={1} justifyContent="center" alignItems="center" direction="row">
                <Button
                  variant="contained" onClick={handleCodeOpen}
                  className={classes.button}
                >
                  API Code (Python)
                </Button>
                <Dialog
                  fullWidth={true}
                  maxWidth={'md'}
                  open={codeOpen}
                  onClose={handleCodeClose}
                >
                  <DialogTitle>
                    {`API Code (Python) for dataset "${selected?.name}"`}
                  </DialogTitle>
                  <DialogContent>
                    <GetDatasetPython dataset={selected} />
                  </DialogContent>
                  <DialogActions>
                    <Button onClick={handleCodeClose} color="primary" autoFocus>
                      Close
                    </Button>
                  </DialogActions>
                </Dialog>
                <React.Fragment>
                  <Button
                    variant="contained" onClick={handleMatlabCodeOpen}
                    className={classes.button}
                  >
                    API Code (MATLAB)
                  </Button>
                  <Dialog
                    fullWidth={true}
                    maxWidth={'md'}
                    open={codeMatlabOpen}
                    onClose={handleMatlabCodeClose}
                  >
                    <DialogTitle>
                      {`API Code (MATLAB) for dataset "${selected?.name}"`}
                    </DialogTitle>
                    <DialogContent>
                      <GetDatasetMatlab dataset={selected} />
                    </DialogContent>
                    <DialogActions>
                      <Button onClick={handleMatlabCodeClose} color="primary" autoFocus>
                        Close
                      </Button>
                    </DialogActions>
                  </Dialog>
                </React.Fragment>
              </Stack>
              {selected !== null && <DatasetChart dataset={selected}/>}
            </Stack>
          }
          subrow_inclusion_rule={(dataset) => selected !== null && dataset.id === selected.id}
          url={`datasets/`}
          styles={classes}
        />
      </Paper>
    </Container>
  );
}
