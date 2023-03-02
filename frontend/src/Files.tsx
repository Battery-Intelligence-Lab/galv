import React, { Fragment } from 'react';
import Container from '@mui/material/Container';
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import Paper from '@mui/material/Paper';
import AsyncTable from './AsyncTable';
import Connection from "./APIConnection";
import {MonitoredPathFields} from "./HarvesterDetail";
import IconButton from "@mui/material/IconButton";
import RefreshIcon from "@mui/icons-material/Refresh";
import useStyles from "./UseStyles";

export type FileFields = {
  url: string;
  id: number;
  monitored_path: string;
  relative_path: string;
  state: string;
  last_observed_time: string;
  last_observed_size: number;
  errors: {
    error: string;
    timestamp: string;
    [key: string]: any;
  }
  datasets: string[];
}

export type FilesProps = { path: MonitoredPathFields }

export default function Files(props: FilesProps) {
  const classes = useStyles();

  const forceReimport = (file: FileFields) => Connection.fetch(`${file.url}reimport/`)

  const datetimeOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric', month: 'numeric', day: 'numeric',
    hour: 'numeric', minute: 'numeric', second: 'numeric',
  };

  const columns = [
    {label: props.path.path, help: 'File path'},
    {label: 'Last Observed Size', help: 'Size of the file in bytes'},
    {label: 'Last Observed Time', help: 'Time file was last scanned'},
    {label: 'State', help: 'File state'},
    {label: 'Datasets', help: 'View datasets linked to this file'},
    {label: 'Force Re-import', help: 'Retry the import operation next time the file is scanned'}
  ]

  const file_state = (file: FileFields) => {
    let state = file.state === 'IMPORT FAILED' ?
      <Typography color='error'>{file.state}</Typography> : <Typography>{file.state}</Typography>
    if (file.errors.length)
      state = <Tooltip title={file.errors[0].error} placement="right">{state}</Tooltip>
    return state
  }

  return (
    <Container maxWidth="lg" className={classes.container} key={`files_for_path${props.path.id}`}>
      <Paper className={classes.paper}>
        <AsyncTable<FileFields>
          classes={classes}
          key="files"
          columns={columns}
          row_generator={(file, context) => [
            <Fragment>{file.relative_path}</Fragment>,
            <Fragment>{file.last_observed_size}</Fragment>,
            <Fragment>{
              Intl.DateTimeFormat('en-GB', datetimeOptions).format(
                Date.parse(file.last_observed_time)
              )}
            </Fragment>,
            <Fragment>{file_state(file)}</Fragment>,
            <Fragment>{file.datasets.length}</Fragment>,
            <Fragment>
              <IconButton onClick={() => forceReimport(file).then(context.refresh)}>
                <RefreshIcon className={classes.refreshIcon} />
              </IconButton>
            </Fragment>
          ]}
          url={`files/?monitored_path__id=${props.path.id}`}
          styles={classes}
        />
      </Paper>
    </Container>
  );
}
