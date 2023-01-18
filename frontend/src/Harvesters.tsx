import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import PaginatedTable, {RowFunProps} from './PaginatedTable';

import HarvesterDetail from './HarvesterDetail';
import Connection from "./APIConnection";
import {isAdmin} from "./Api";

export type HarvesterWriteableFields = {
  name: string;
  sleep_time: number;
}

export type HarvesterFields = HarvesterWriteableFields & {
  url: string;
  id: number;
  last_check_in: string | null;
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

export default function Harvesters() {
  const classes = useStyles();

  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const [selected, setSelected] = useState<HarvesterFields|null>(null)
  const userIsAdmin = isAdmin()

  const updateHarvester = (data: any) => {
    const insert_data: HarvesterWriteableFields = {
      name: data.name,
      sleep_time: data.sleep_time
    }
    Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(() => setLastUpdated(new Date()))
  };

  const deleteHarvester = () => {
    if (selected !== null)
      Connection.fetch(selected.url, {method: 'DELETE'})
        .then(() => setLastUpdated(new Date()))
        .then(() => setSelected(null))
  };

  function table_row_generator(row: any) {
    return (<MyTableRow
        key={row.id}
        savedRow={row}
        onRowSave={updateHarvester}
        selected={selected !== null && selected.id === row.id}
        onSelectRow={setSelected}
        disableSave={!userIsAdmin}
    />)
  }

  function MyTableRow(props: RowFunProps<HarvesterFields>) {
    const classes = useStyles();
    const [row, setRow] = useState<HarvesterFields>({
      id: -1,
      url: "",
      name: "",
      last_check_in: null,
      sleep_time: 3600
    })
    const [dirty, setDirty] = useState<boolean>(false)

    useEffect(() => {
      if (!dirty && props.savedRow) {
        setRow(props.savedRow);
      }
    }, [dirty, props.savedRow]);

    let useRow = row;
    if (row.id === -1 && props.savedRow)
      useRow = props.savedRow;

    const Icon = props.addIcon ? <AddIcon/> : <SaveIcon/> ;

    return (
        <React.Fragment>
          <TableRow
              onClick={() => {props.onSelectRow(props.savedRow);}}
              hover
              selected={props.selected}
          >
            <TableCell component="th" scope="row">
              {props.savedRow?.id || ""}
            </TableCell>

            <TableCell>
              <TextField
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                    placeholder: "New Harvester"
                  }}
                  value={useRow.name}
                  onChange={(e) => {
                    setDirty(true);
                    setRow({...row, name: e.target.value});
                  }}
              >
              </TextField>
            </TableCell>
            <TableCell component="th" scope="row">
              {(props.savedRow?.last_check_in &&
                  Intl.DateTimeFormat('en-GB',
                      { dateStyle: 'long', timeStyle: 'long' }).format(
                      Date.parse(props.savedRow.last_check_in)
                  )) || (<Typography color='grey'>None</Typography>)}
            </TableCell>
            <TableCell>
              <TextField
                  type="number"
                  placeholder="60"
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  value={useRow.sleep_time ? useRow.sleep_time : ''}
                  onChange={(e) => {
                    setDirty(true);
                    setRow({...row, sleep_time: parseInt(e.target.value)});
                  }}
              >
              </TextField>
            </TableCell>
            <TableCell align="right">
              <Tooltip title={props.addIcon? "Add new Harvester" : "Save changes to Harvester"}>
        <span>
        <IconButton
            disabled={props.disableSave || !dirty}
            onClick={() => {
              props.onRowSave(row);
              setDirty(false);
            }}
        >
          { Icon }
        </IconButton>
        </span>
              </Tooltip>
            </TableCell>
          </TableRow>
        </React.Fragment>
    )
  }

  const column_headings = [
    {label: 'ID', help: 'Harvester id in database'},
    {label: 'Name', help: 'Harvester name'},
    {label: 'Last Check In', help: 'Datetime of last harvester run that successfully contacted the database'},
    {label: 'Sleep Time (s)', help: 'If set, harvester is run every day on this hour'},
    {label: 'Save', help: 'Click to save edits to a row'},
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

  const paginated_table = (<PaginatedTable
    header={(<TableHead>{table_head}</TableHead>)}
    row_fun= {table_row_generator}
    initial_url={`harvesters/`}
    styles={classes}
    last_updated={lastUpdated}
  />)

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
      {paginated_table}
    <Tooltip title="Delete selected harvester">
      <span>
    <IconButton 
      disabled={!userIsAdmin || selected === null}
      aria-label="delete" 
      onClick={deleteHarvester}
    >
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    </Paper>
    {selected !== null && <HarvesterDetail harvester={selected} />}
    </Container>
  );
}
