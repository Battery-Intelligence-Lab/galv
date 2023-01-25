
import React, {useEffect, useState, Fragment} from "react";
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
import Connection from "./APIConnection"
import AsyncTable, {CellContext} from "./AsyncTable"
import { Paper } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import {UserSet} from "./UserRoleSet";
import SettingsIcon from "@mui/icons-material/Settings";

export type DatasetFields = {
  url: string;
  id: number;
  name: string;
  type: string;
  date: string;
  cell: string;
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

  const updateRow = (data: DatasetFields) => {
    const insert_data = {name: data.name, type: data.type, purpose: data.purpose}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
  }

  const columns = [
    {label: 'ID', help: 'Unique ID in database'},
    {label: 'Date', help: 'Date of Test'},
    {label: 'Name', help: ''},
    {label: 'Type', help: 'File type determined by Harvester'},
    {label: 'Purpose', help: 'Short description of dataset purpose'},
    {label: 'Cell', help: 'Cell that generated the dataset'},
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

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable
          columns={columns}
          rows={[
            (dataset: DatasetFields) => <Fragment>{dataset.id}</Fragment>,
            (dataset: DatasetFields) => <Fragment>{dataset.date}</Fragment>,
            // these fields have the same shape, so condense the code.
            // as const stops TypeScript from complaining about strings assigned to keyof DatasetFields
            ...(['name', 'type', 'purpose'] as const).map(
              (n) => ((dataset: DatasetFields, context: CellContext) => <Fragment>
                <TextField
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    }
                  }}
                  name={n}
                  value={dataset[n]}
                  onChange={context.update} />
              </Fragment>)
            ),
            (dataset: DatasetFields) => <Fragment>{dataset.cell}</Fragment>,
            (dataset: any) => <Fragment key="select">
              <IconButton onClick={() => selected?.id === dataset.id? setSelected(null) : setSelected(dataset)}>
                <SettingsIcon color={selected?.id === dataset.id? 'info' : undefined} />
              </IconButton>
            </Fragment>,
            (dataset: any, context) => <Fragment key="save">
              <IconButton
                disabled={!dataset._changed}
                onClick={() => updateRow(dataset).then(context.refresh)}
              >
                <SaveIcon />
              </IconButton>
            </Fragment>
          ]}
          initial_url={`datasets/?all=true`}
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
