import React, { useEffect, useState } from 'react';
import { makeStyles } from '@mui/styles'
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import Container from '@mui/material/Container';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Paper from '@mui/material/Paper';
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

  useEffect(() => {
    files(path.id).then((response) => {
      if (response.ok) {
        response.json().then((result) => {
          setFileData(result.sort((arg1, arg2) => arg1.id - arg2.id));
        });
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
            <TableRow key={row.path}>
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
