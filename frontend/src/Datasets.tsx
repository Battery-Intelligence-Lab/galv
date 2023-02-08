
import React, {useEffect, useState, Fragment, ReactElement} from "react";
import Container from '@mui/material/Container';
import { makeStyles } from '@mui/styles'
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
import Select from "@mui/material/Select";
import SaveIcon from "@mui/icons-material/Save";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import {UserSet} from "./UserRoleSet";
import SettingsIcon from "@mui/icons-material/Settings";
import {CellFields} from "./CellList";
import MenuItem from "@mui/material/MenuItem";
import CircularProgress from "@mui/material/CircularProgress";
import {EquipmentFields} from "./Equipment";
import OutlinedInput from "@mui/material/OutlinedInput";
import Box from "@mui/material/Box";
import Chip from "@mui/material/Chip";

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

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  table: {
    minWidth: 650,
  },
  resize: {
    fontSize: '11pt',
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
    {label: 'ID', help: 'Unique ID in database'},
    {label: 'Date', help: 'Date of Test'},
    {label: 'Name', help: ''},
    {label: 'Type', help: 'File type determined by Harvester'},
    {label: 'Purpose', help: 'Short description of dataset purpose'},
    {label: 'Cell', help: 'Cell that generated the dataset'},
    {label: 'Equipment', help: 'Equipment used to generate the dataset'},
    {label: 'Details', help: 'Advanced dataset properties'},
    {label: 'Save', help: 'Save changes'},
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
      if (!cellListLoading)
        items.push(<MenuItem key="none" value={-1}><em>None</em></MenuItem>)
    }
    if (cellListLoading)
      items.push(<MenuItem key="loading" value={-1} disabled={true}><CircularProgress/></MenuItem>)
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
      if (!equipmentListLoading)
        items.push(<MenuItem key="none" value={-1}><em>None</em></MenuItem>)
    }
    if (equipmentListLoading)
      items.push(<MenuItem key="loading" value={-1} disabled={true}><CircularProgress/></MenuItem>)
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
            <Fragment>{dataset.id}</Fragment>,
            <Fragment>
              {
                Intl.DateTimeFormat(
                  'en-GB',
                  {dateStyle: 'long', timeStyle: 'long'})
                  .format(Date.parse(dataset.date))
              }
            </Fragment>,
            // these fields have the same shape, so condense the code.
            // as const stops TypeScript from complaining about strings assigned to keyof DatasetFields
            ...(['name', 'type', 'purpose'] as const).map(
              (n) => <Fragment>
                <TextField
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    }
                  }}
                  name={n}
                  value={dataset[n]}
                  onChange={context.update} />
              </Fragment>
            ),
            <Fragment>
              <Select
                id={`cell-select-${dataset.id}`}
                name={'cell'}
                value={dataset.cell?.id || ''}
                onChange={
                  (e) => context.update_direct('cell', cellList?.find(c => c.id === e.target.value) || null)
                }
              >
                {get_cell_items(dataset)}
              </Select>
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
            <Fragment key="select">
              <IconButton onClick={() => selected?.id === dataset.id? setSelected(null) : setSelected(dataset)}>
                <SettingsIcon color={selected?.id === dataset.id? 'info' : undefined} />
              </IconButton>
            </Fragment>,
            <Fragment key="save">
              <IconButton
                disabled={!context.value_changed}
                onClick={() => updateRow(dataset, context).then(context.refresh)}
              >
                <SaveIcon />
              </IconButton>
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
