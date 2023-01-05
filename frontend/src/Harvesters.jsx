import React, { useEffect, useState } from 'react';
import TextField from '@mui/material/TextField';
import { makeStyles } from '@mui/styles'
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import Tooltip from '@mui/material/Tooltip';
import AddIcon from '@mui/icons-material/Add';
import IconButton from '@mui/material/IconButton';
import TableCell from '@mui/material/TableCell';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import TableHead from '@mui/material/TableHead';
import DeleteIcon from '@mui/icons-material/Delete';
import TableRow from '@mui/material/TableRow';
import PaginatedTable from './PaginatedTable';

import HarvesterDetail from './HarvesterDetail';
import { url,
  run_harvester, harvesters, add_harvester,
  update_harvester, delete_harvester, isAdmin
} from './Api'

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
}));

export default function Harvesters() {
  const classes = useStyles();

  const [selected, setSelected] = useState({id: null})
  const userIsAdmin = isAdmin()

  const addNewHarvester = (data) => {
    add_harvester({name: data.name, sleep_time: data.sleep_time});
  };
  const deleteHarvester= () => {
    delete_harvester(selected.id);
  };
  const updateHarvester= (value) => {
    update_harvester(value.id, value);
  };

  const runSelectedHarvester = () => {
    run_harvester(selected.id);
  };

  function table_row_generator(row) {
    return  (<MyTableRow
        key={row.id}
        savedRow={row}
        onRowSave={updateHarvester}
        selected={selected.id === row.id}
        onSelectRow={setSelected}
        disableSave={!userIsAdmin}
    />)
  }

  function MyTableRow({savedRow, onRowSave, selected, onSelectRow, disableSave, addIcon}) {
    const classes = useStyles();
    const [row, setRow] = useState([])
    const [dirty, setDirty] = useState(false)

    useEffect(() => {
      if (!dirty) {
        setRow(savedRow);
      }
    }, [dirty, savedRow]);


    let useRow = row;
    if (useRow.id === undefined) {
      useRow = savedRow;
    }

    const Icon = addIcon ? <AddIcon/> : <SaveIcon/> ;

    return (
        <React.Fragment>
          <TableRow
              onClick={() => {onSelectRow(savedRow);}}
              hover
              selected={selected}
          >
            <TableCell component="th" scope="row">
              {savedRow.id}
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
              {(savedRow.is_running && (<Typography color='secondary'>Yes</Typography>)) ||
                  (<Typography color='grey'>No</Typography>)
              }
            </TableCell>
            <TableCell component="th" scope="row">
              {(savedRow.last_successful_run &&
                  Intl.DateTimeFormat('en-GB',
                      { dateStyle: 'long', timeStyle: 'long' }).format(
                      Date.parse(savedRow.last_successful_run)
                  )) || (<Typography color='grey'>None</Typography>)}
            </TableCell>
            <TableCell>
              <TextField
                  type="number"
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  value={useRow.sleep_time ? useRow.sleep_time : ''}
                  onChange={(e) => {
                    setDirty(true);
                    setRow({...row, sleep_time: e.target.value});
                  }}
              >
              </TextField>
            </TableCell>
            <TableCell align="right">
              <Tooltip title={addIcon? "Add new Harvester" : "Save changes to Harvester"}>
        <span>
        <IconButton
            disabled={disableSave || !dirty}
            onClick={() => {
              onRowSave(row);
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

  const new_row = (
      <MyTableRow
          key="new"
          savedRow={{
            id: null,
            name: "",
            last_successful_run: "",
            is_running: false,
            sleep_time: false
          }}
          onRowSave={addNewHarvester}
          selected={false}
          onSelectRow={() => {}}
          disableSave={false}
          addIcon={true}
      />
  )

  const column_headings = [
    {label: 'ID', help: 'Harvester id in database'},
    {label: 'Name', help: 'Harvester name'},
    {label: 'Is Running', help: 'Displays "True" if harvester is currently running'},
    {label: 'Last Completed Run', help: 'Datetime of last harvester run that successfully ran until completion'},
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

  const isSelected = selected.id !== null;

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
      <PaginatedTable data={{
        header: (<TableHead>{table_head}</TableHead>),
        row_fun: table_row_generator,
        initial_url: `${url}harvesters/`,
        new_entry_row: new_row,
        styles: classes,
      }}/>
    <Tooltip title="Delete selected harvester">
      <span>
    <IconButton 
      disabled={!userIsAdmin || !isSelected} 
      aria-label="delete" 
      onClick={deleteHarvester}
    >
      <DeleteIcon />
    </IconButton>
      </span>
    </Tooltip>
    <Tooltip title="Run the selected harvester">
      <span>
      <IconButton 
        disabled={!userIsAdmin || !isSelected || selected.is_running} 
        onClick={runSelectedHarvester}
      >
      <PlayArrowIcon/>
    </IconButton>
    </span>
    </Tooltip>
    </Paper>
    {isSelected &&
      <HarvesterDetail harvester={selected} />
    }
    </Container>
  );
}
