import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { DataGrid, GridRowsProp, GridColDef } from '@material-ui/data-grid';
import Paper from '@material-ui/core/Paper';
import Typography from '@material-ui/core/Typography';
import { makeStyles } from '@material-ui/core/styles';
import {harvester, monitored_path} from './Api';

const useStyles = makeStyles((theme) => ({
  title: {
    flexGrow: 1,
  },
}));


export default function HarvesterDetail(props) {
  const classes = useStyles();
  let { id } = useParams();

  const [data, setData] = useState([])

  useEffect(() => {
    harvester(id).then((response) => {
      if (response.ok) {
        return response.json().then(setData);
      }
    });
  }, []);

  const [paths, setPaths] = useState([]);

  useEffect(() => {
    monitored_path(id).then((response) => {
      if (response.ok) {
        return response.json().then(setPaths);
      }
    });
  }, []);

  const columns: GridColDef[] = [
    { field: 'path', headerName: 'Path', width: 230 },
    { field: 'monitored_for', headerName: 'Monitored For', width: 230 },
  ];

  const rows: GridRowsProp = paths.map((r) => {
    console.log(r);
    return {
      id: r.monitor_path_id,
      path: r.path,
      monitored_for: r.monitored_for,
    };
  });
  console.log(rows);

  return (
    <Paper>
    <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
      Monitored Paths for "{data.machine_id}"
    </Typography>
    <div style={{ height: 300, width: '100%' }}>
      <DataGrid rows={rows} columns={columns} pageSize={5} />
    </div>
    </Paper>
  );
}
