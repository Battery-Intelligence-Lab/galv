import React, { useEffect, useState, useCallback, useRef } from "react";
import Container from '@material-ui/core/Container';
import { useParams } from "react-router-dom";
import { DataGrid, GridRowsProp, GridColDef } from '@material-ui/data-grid';
import Typography from '@material-ui/core/Typography';
import IconButton from '@material-ui/core/IconButton';
import AddIcon from '@material-ui/icons/Add';
import DeleteIcon from '@material-ui/icons/Delete';
import { makeStyles } from '@material-ui/core/styles';
import Tooltip from '@material-ui/core/Tooltip';
import {
  harvester, monitored_path, 
  update_monitored_path, add_monitored_path,
  del_monitored_path
} from './Api';

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
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
  }, [id]);

  const [paths, setPaths] = useState([]);

  const refreshPaths = () => {
    monitored_path(id).then((response) => {
      if (response.ok) {
        return response.json().then(setPaths);
      }
    });
  };

  useEffect(refreshPaths, 
  // eslint-disable-next-line react-hooks/exhaustive-deps
  []);

  const handleEditCellChangeCommitted = useCallback(
    ({ id, field, props }) => {
      console.log('change committed', field)
      let path = {};
      path[field] = props.value;
      update_monitored_path(id, path)
    },
    [],
  );

  const addNewPath = () => {
    return add_monitored_path(
      {monitored_for: [], path: '', harvester_id: id}
    ).then(refreshPaths);
  };

  let select = useRef([]);

  const handleSelectionChange = (e) => {
    console.log('handleSelectionChange', e.selectionModel)
    select.current = e.selectionModel;
  };

  const removeSelectedPaths = () => {
    Promise.all(select.current.map((id) => {
      console.log('del', id);
      return del_monitored_path(id)    
    })).then(refreshPaths);
  };


  const columns: GridColDef[] = [
    { field: 'id', headerName: 'ID' },
    { field: 'path', editable: true, headerName: 'Path', width: 230 },
    { field: 'monitored_for', editable: true, headerName: 'Monitored For', width: 230 },
  ];

  const rows: GridRowsProp = paths.map((r) => {
    console.log(r);
    return {
      id: r.monitor_path_id,
      path: r.path,
      monitored_for: JSON.stringify(r.monitored_for),
    };
  });
  console.log(rows);

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Typography variant="h6">
      Configuration for "{data.machine_id}"
    </Typography>
    <Typography variant="h6" color="primary">
      Monitored Paths:
    </Typography>
    <div style={{ height: 300, width: '100%' }}>
      <DataGrid 
        rows={rows} columns={columns} 
        pageSize={5} checkboxSelection
        onEditCellChangeCommitted={handleEditCellChangeCommitted}
        onSelectionModelChange={handleSelectionChange}
      />
    </div>

    <Tooltip title="Add new path">
      <IconButton aria-label="add" onClick={addNewPath}>
      <AddIcon/>
    </IconButton>
    </Tooltip>
    <Tooltip title="Delete selected paths">
    <IconButton aria-label="delete" onClick={removeSelectedPaths}>
      <DeleteIcon />
    </IconButton>
    </Tooltip>
    </Container>
  );
}
