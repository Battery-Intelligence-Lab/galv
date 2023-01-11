import React, { useState } from 'react';
import { makeStyles } from '@mui/styles'
import Container from '@mui/material/Container';
import TableCell from '@mui/material/TableCell';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
import PaginatedTable from './PaginatedTable';
import Connection from "./APIConnection";
import {MonitoredPathFields} from "./HarvesterDetail";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import DatasetIcon from '@mui/icons-material/Dataset';
import IconButton from "@mui/material/IconButton";
import RefreshIcon from "@mui/icons-material/Refresh";


const useStyles = makeStyles((theme) => ({
  head: {
    backgroundColor: theme.palette.primary.light,
  },
  headCell: {
    color: theme.palette.common.black,
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  table: {
    minWidth: 650,
  },
  paper: {}
}));

export type FileFields = {
  url: string,
  id: number,
  monitored_path: string,
  relative_path: string,
  state: string,
  last_observed_time: string,
  last_observed_size: number,
  datasets: string[]
}

export type FilesProps = {
  path: MonitoredPathFields,
  lastUpdated: Date
}

export default function Files(props: FilesProps) {
  const classes = useStyles();
  const [lastUpdated, setLastUpdated] = useState<Date>(props.lastUpdated)

  const forceReimport = (file: FileFields) => {
    Connection.fetch(`${file.url}reimport/`)
      .then(() => setLastUpdated(new Date()))
  }

  const datetimeOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: 'numeric', day: 'numeric',
    hour: 'numeric', minute: 'numeric', second: 'numeric',
  };

  const column_headings = [
    {label: props.path.path, help: 'File path'},
    {label: 'Last Observed Size', help: 'Size of the file in bytes'},
    {label: 'Last Observed Time', help: 'Time file was last scanned'},
    {label: 'State', help: 'File state'},
    {label: 'Datasets', help: 'View datasets linked to this file'},
    {label: 'Force Re-import', help: 'Retry the import operation next time the file is scanned'}
  ]

  const table_head = column_headings.map(heading => (
    <TableCell key={heading.label} className={classes.headCell}>
      <Tooltip title={heading.help}>
        <Typography>
          {heading.label}
        </Typography>
      </Tooltip>
    </TableCell>
  ))

  function row_fun(file: FileFields) {
    return (
      <React.Fragment>
        <TableRow>
          <TableCell align="right" key={"Path"}>{file.relative_path}</TableCell>
          <TableCell key={"Size"}>{file.last_observed_size}</TableCell>
          <TableCell align="right">
            {
              Intl.DateTimeFormat('en-GB', datetimeOptions).format(
                Date.parse(file.last_observed_time)
              )
            }
          </TableCell>
          <TableCell>{file.state}</TableCell>
          <TableCell>{file.datasets.map(d => (<IconButton><DatasetIcon /></IconButton>))}</TableCell>
          <TableCell><IconButton onClick={() => forceReimport(file)}><RefreshIcon /></IconButton></TableCell>
        </TableRow>
      </React.Fragment>
    )
  }

  return (
    <Container maxWidth="lg" className={classes.container} key={`files_for_path${props.path.id}`}>
    <Paper className={classes.paper}>
      <PaginatedTable
        header={(<TableHead>{table_head}</TableHead>)}
        row_fun={row_fun}
        initial_url={`files/?monitored_path__id=${props.path.id}`}
        styles={classes}
        last_updated={lastUpdated}
      />
    </Paper>
    </Container>
  );
}
