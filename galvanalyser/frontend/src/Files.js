import React, { useEffect, useState } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import Container from '@material-ui/core/Container';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { files } from './Api'


const useStyles = makeStyles((theme) => ({
  head: {
    backgroundColor: theme.palette.primary.light,
  },
  headCell: {
    color: theme.palette.common.white,
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  table: {
    minWidth: 650,
  },
}));

export default function Files({ path }) {
  const classes = useStyles();

  const [fileData, setFileData] = useState([])
  console.log('path', path);

  useEffect(() => {
    files(path.monitor_path_id).then((response) => {
      if (response.ok) {
        response.json().then(setFileData);
      }
    });
  }, [path]);

  const datetimeOptions = {
    year: 'numeric', month: 'numeric', day: 'numeric',
    hour: 'numeric', minute: 'numeric', second: 'numeric',
  };

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Paper className={classes.paper}>
    <TableContainer>
      <Table className={classes.table}>
        <TableHead className={classes.head}>
          <TableRow>
            <TableCell className={classes.headCell}>Observed File</TableCell>
            <TableCell className={classes.headCell} align="right">Last Observed Size</TableCell>
            <TableCell className={classes.headCell} align="right">Last Observed Time</TableCell>
            <TableCell className={classes.headCell} align="right">State</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {fileData.map((row) => (
            <TableRow key={row.name}>
              <TableCell component="th" scope="row">
                {row.path}
              </TableCell>
              <TableCell align="right">
                {row.last_observed_size}
              </TableCell>
              <TableCell align="right">
              {
                Intl.DateTimeFormat('en-GB', datetimeOptions).format(
                  Date.parse(row.last_observed_time)
                )
              }
              </TableCell>
              <TableCell align="right">
                {row.file_state}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    </Paper>
    </Container>
  );
}
