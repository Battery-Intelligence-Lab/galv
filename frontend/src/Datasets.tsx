import React, {useEffect, useState, Fragment, ReactElement} from "react";
import Container from '@mui/material/Container';
import Button from '@mui/material/Button';
import { useNavigate } from "react-router-dom";
import GetDatasetPython from "./GetDatasetPython"
import GetDatasetMatlab from "./GetDatasetMatlab"
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import Connection, {APIConnection} from "./APIConnection"
import AsyncTable, {RowGeneratorContext} from "./AsyncTable"
import Paper from "@mui/material/Paper";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import {UserSet} from "./UserRoleSet";
import {CellFields} from "./CellList";
import MenuItem from "@mui/material/MenuItem";
import CircularProgress from "@mui/material/CircularProgress";
import {EquipmentFields} from "./Equipment";
import OutlinedInput from "@mui/material/OutlinedInput";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import Grid from "@mui/material/Grid";
import InputLabel from "@mui/material/InputLabel";
import useStyles from "./UseStyles";
import ActionButtons from "./ActionButtons";

export type DatasetFields = {
  url: string;
  id: number;
  name: string;
  type: string;
  date: string;
  cell: CellFields | null;
  equipment: EquipmentFields[];
  purpose: string;
  user_sets: UserSet[];
}

export default function Datasets() {
  const classes = useStyles();
  const [selected, setSelected] = useState<DatasetFields|null>(null)
  const [cellListLoading, setCellListLoading] = useState<boolean>(true)
  const [cellList, setCellList] = useState<CellFields[]>([])
  const [equipmentListLoading, setEquipmentListLoading] = useState<boolean>(true)
  const [equipmentList, setEquipmentList] = useState<EquipmentFields[]>([])

  useEffect(() => {
    Connection.fetch('cells/?all=true', {}, 0)
      .then(APIConnection.get_result_array)
      .then(r => {
        if (typeof r === 'number')
          throw new Error(`cells/?all=true -> ${r}`)
        // @ts-ignore
        setCellList(r)
        setCellListLoading(false)
      })
  }, [])

  useEffect(() => {
    Connection.fetch('equipment/?all=true', {}, 0)
      .then(APIConnection.get_result_array)
      .then(r => {
        if (typeof r === 'number')
          throw new Error(`equipment/?all=true -> ${r}`)
        // @ts-ignore
        setEquipmentList(r)
        setEquipmentListLoading(false)
      })
  }, [])

  const updateRow = (data: DatasetFields, context: RowGeneratorContext<DatasetFields>) => {
    context.mark_loading(true)
    const insert_data: any = {
      name: data.name,
      type: data.type,
      cell: data.cell?.url || null,
      equipment: data.equipment.map(e => e.url)
    }
    if (data.purpose) insert_data.purpose = data.purpose
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  }

  const columns = [
    {label: 'Date', help: 'Date of Test'},
    {label: 'Properties', help: ''},
    {label: 'Equipment', help: 'Equipment used to generate the dataset'},
    {label: 'Actions', help: 'Inspect / Save dataset'}
  ]

  const navigate = useNavigate();

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
    const menuItem = (cell: CellFields) => <MenuItem key={cell.id} value={cell.id}>{cell.display_name}</MenuItem>
    const items: ReactElement[] = []
    if (dataset?.cell) {
      items.push(menuItem(dataset.cell))
    }
    if (cellListLoading)
      items.push(<MenuItem key="loading" value="" disabled={true}><CircularProgress/></MenuItem>)
    else
      items.push(<MenuItem key="na" value=""><em>None</em></MenuItem>)
    if (cellList.length)
      items.push(...cellList.filter(c => c.id !== dataset.cell?.id).map(menuItem))
    if (!items.length)
      items.push(<MenuItem key="empty" disabled={true}><em>No cells defined</em></MenuItem>)
    return items
  }

  const get_equipment_items = (dataset: DatasetFields) => {
    const menuItem = (equipment: EquipmentFields) =>
      <MenuItem key={equipment.id} value={equipment.id}>{equipment.name}</MenuItem>
    const items: ReactElement[] = []
    const current_equipment_ids: number[] = []
    if (dataset?.equipment) {
      items.push(...dataset.equipment.map(e => menuItem(e)))
      current_equipment_ids.push(...dataset.equipment.map(e => e.id))
    }
    if (equipmentListLoading)
      items.push(<MenuItem key="loading" value="" disabled={true}><CircularProgress/></MenuItem>)
    else
      items.push(<MenuItem key="none" value=""><em>None</em></MenuItem>)
    if (equipmentList.length)
      items.push(...equipmentList.filter(e => !current_equipment_ids.includes(e.id)).map(menuItem))
    if (!items.length)
      items.push(<MenuItem key="empty" disabled={true}><em>No equipment defined</em></MenuItem>)
    return items
  }

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<DatasetFields>
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
                </Grid>
                <Grid container spacing={1} pt={1}>
                  <Grid item>
                    <Tooltip title="Purpose for which data were collected" placement="right">
                      <TextField
                        InputProps={{classes: {input: classes.resize}}}
                        name="purpose"
                        label="Purpose"
                        fullWidth
                        value={dataset.purpose}
                        onChange={context.update}
                      />
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <FormControl>
                      <InputLabel key='label' id={`cell-select-label-${dataset.id}`}>Cell</InputLabel>
                      <Select
                        key='select'
                        id={`cell-select-${dataset.id}`}
                        name="cell"
                        value={dataset.cell?.id || ''}
                        sx={{minWidth: 100}}
                        onChange={
                          (e) => context.update_direct('cell', cellList?.find(c => c.id === e.target.value) || null)
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
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {selected.map((value) => (
                      <Chip key={value} label={dataset.equipment.find(e => e.id === value)?.name || '???'} />
                    ))}
                  </Box>
                )}
                name={'equipment'}
                sx={{minWidth: 100}}
                multiple
                value={dataset?.equipment?.map(e => e.id) || []}
                onChange={
                  (e) => {
                    const value: number[] = typeof e.target.value === 'string' ?
                      e.target.value.split(',').map(i => parseInt(i)) : e.target.value
                    context.update_direct(
                      'equipment',
                      equipmentList?.filter(eq => value.includes(eq.id))
                    )
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
          url={`datasets/?all=true`}
          styles={classes}
        />
      </Paper>
      {selected !== null &&
          <Button variant="contained"
                  className={classes.button}
                  onClick={()=>{navigate(`/dataset/${selected.id}`);}}
          >
              Edit Metadata
          </Button>
      }
      {selected !== null &&
          <React.Fragment>
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
                    {`API Code (Python) for dataset "${selected.name}"`}
                  </DialogTitle>
                  <DialogContent>
                      <GetDatasetPython dataset={selected.id} />
                  </DialogContent>
                  <DialogActions>
                      <Button onClick={handleCodeClose} color="primary" autoFocus>
                          Close
                      </Button>
                  </DialogActions>
              </Dialog>
          </React.Fragment>
      }
      {selected !== null &&
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
                    {`API Code (MATLAB) for dataset "${selected.name}"`}
                  </DialogTitle>
                  <DialogContent>
                      <GetDatasetMatlab dataset={selected.id} />
                  </DialogContent>
                  <DialogActions>
                      <Button onClick={handleMatlabCodeClose} color="primary" autoFocus>
                          Close
                      </Button>
                  </DialogActions>
              </Dialog>
          </React.Fragment>
      }
    </Container>
  );
}
