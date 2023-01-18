
import React, {useEffect, useState} from "react";
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
import PaginatedTable, {RowFunProps} from "./PaginatedTable"
import TableCell from "@mui/material/TableCell";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import TableHead from "@mui/material/TableHead";
import { Paper } from "@mui/material";
import SaveIcon from "@mui/icons-material/Save";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import IconButton from "@mui/material/IconButton";
import {UserSet} from "./UserRoleSet";

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

function MyTableRow(props: RowFunProps<DatasetFields>) {
  const classes = useStyles();
  const [row, setRow] = useState<DatasetFields>({
    url: "", id: -1, name: '', type: '', date: '', cell: '', purpose: '', user_sets: []
  })
  const [dirty, setDirty] = useState<boolean>(false)

  const rowUnchanged = Object.keys(row).reduce((a, k) => {
    //@ts-ignore
    return a && row[k] === props.savedRow[k];
  }, true);

  useEffect(() => {
    if (!dirty && props.savedRow) {
      setRow(props.savedRow);
    }
  }, [dirty, props.savedRow]);

  let useRow = row;
  if (row.id === -1 && props.savedRow)
    useRow = props.savedRow;

  const setValue = (key: string) => (e: any) => {
    setDirty(true);
    setRow({...useRow, [key]: e.target?.value});
  };

  const Icon = <SaveIcon/>;

  return (
    <React.Fragment>
      <TableRow
        onClick={() => {props.onSelectRow(props.savedRow);}}
        hover
        selected={props.selected}
      >
        <TableCell align={"right"}>{useRow.id}</TableCell>
        <TableCell>{useRow.date}</TableCell>
        <TableCell align="right" key={"name"}>
          <TextField
            InputProps={{
              classes: {
                input: classes.resize,
              }
            }}
            value={useRow.name}
            onChange={setValue('name')} />
        </TableCell>
        <TableCell align="right" key={"type"}>
          <TextField
            InputProps={{
              classes: {
                input: classes.resize,
              }
            }}
            value={useRow.type}
            onChange={setValue('type')} />
        </TableCell>
        <TableCell align="right" key={"purpose"}>
          <TextField
            InputProps={{
              classes: {
                input: classes.resize,
              }
            }}
            value={useRow.purpose}
            onChange={setValue('purpose')} />
        </TableCell>
        <TableCell>{useRow.cell}</TableCell>
        <TableCell align="right" key={"Save"}>
          <Tooltip title={props.addIcon? "Add new Path" : "Save changes to Path"}>
        <span>
        <IconButton
          disabled={props.disableSave || rowUnchanged}
          onClick={() => {
            setDirty(false);
            props.onRowSave(row);
          }}
        >
          {Icon}
        </IconButton>
        </span>
          </Tooltip>
        </TableCell>
      </TableRow>
    </React.Fragment>
  )
}

export default function Datasets() {
  const classes = useStyles();
  const [selected, setSelected] = useState<DatasetFields|null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const updateRow = (data: DatasetFields) => {
    const insert_data = {name: data.name, type: data.type, purpose: data.purpose}
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

  const column_headings = [
    {label: 'ID', help: 'Unique ID in database'},
    {label: 'Date', help: 'Date of Test'},
    {label: 'Name', help: ''},
    {label: 'Type', help: 'File type determined by Harvester'},
    {label: 'Purpose', help: 'Short description of dataset purpose'},
    {label: 'Cell', help: 'Cell that generated the dataset'},
    {label: 'Save', help: 'Save changes'},
  ]

  const table_head = column_headings.map(heading => (
    <TableCell key={heading.label}>
      <Tooltip title={heading.help}>
        <Typography>
          {heading.label}
        </Typography>
      </Tooltip>
    </TableCell>
  ))
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
        <PaginatedTable
          header={(<TableHead>{table_head}</TableHead>)}
          row_fun={(row: DatasetFields) => (
            <MyTableRow
              key={row.id}
              savedRow={row}
              onRowSave={updateRow}
              selected={selected !== null && selected.id === row.id}
              onSelectRow={setSelected}
            />
          )}
          initial_url={`datasets/`}
          styles={classes}
          last_updated={lastUpdated}
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
