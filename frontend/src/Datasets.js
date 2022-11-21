
import React, {useEffect, useState} from "react";
import { DataGrid, GridRowsProp, GridColDef } from '@material-ui/data-grid';
import Container from '@material-ui/core/Container';
import { datasets } from './Api';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import { useHistory } from "react-router-dom";
import GetDatasetPython from "./GetDatasetPython"
import GetDatasetMatlab from "./GetDatasetMatlab"
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';


const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    height: '100%',
  },
  button: {
    margin: theme.spacing(1),
  }
}));



export default function Datasets() {
  const [data, setData] = useState(null)
  const classes = useStyles();
  const history = useHistory();

  const [select, setSelect] = useState(null)

  // TODO: use controlled selectionModel, cause this api is changin...
  const handleSelectionChange = (e) => {
    if (e.selectionModel) {
      if (e.selectionModel.length > 0) {
        setSelect(e.selectionModel[0]);
      }
    } else {
      if (e.length > 0) {
        setSelect(e[0]);
      }
    }
  };

  useEffect(() => {
    datasets().then((response) => {
      if (response.ok) {
        return response.json().then(data => {
          setData(data.sort((a, b) => {
            if (a.date > b.date) {
              return -1;
            }
            if (a.date < b.date) {
              return 1;
            }
            return 0;
          }));
        });
      }
    });
  }, [])

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

 

  const columns: GridColDef[] = [
    { field: 'dataset_id', headerName: 'ID', width: 70},
    { field: 'name', headerName: 'Name', flex: true},
    { 
      field: 'date', headerName: 'Date', width: 110,
      valueFormatter: (params: GridValueFormatterParams) => {
        return Intl.DateTimeFormat('en-GB').format(params.value);
      }
    },
    { field: 'type', headerName: 'Type', width: 90 },
    { field: 'cell', headerName: 'Cell', width: 100 },
    { field: 'owner', headerName: 'Owner', width: 120 },
    { field: 'purpose', headerName: 'Purpose', width: 250 },
    { field: 'metadata', headerName: 'Metadata', type: 'boolean', width: 120 },
  ];

  let rows: GridRowsProp = []
  if ( data ) {
    rows = data.map((d, i) => {
      return {
        id: i,
        dataset_id: d.id,
        name: d.name,
        type: d.type,
        date: Date.parse(d.date),
        cell: d.cell ? d.cell.name : '',
        owner: d.owner ? d.owner.username : '',
        purpose: d.purpose,
        metadata: !(!d.cell || !d.owner || !d.purpose || d.equipment.length === 0)
      };
    });
  }


  let autoHeight = true;
  let divStyle = { width: '100%' };
  console.log('datasets', rows)
  

  return (
    <Container maxWidth="lg" className={classes.container}>
      <div style={divStyle}>
      <DataGrid 
        rows={rows} columns={columns} 
        density='compact'
        autoPageSize
        loading={ !data }
        rowHeight={38}
        autoHeight={autoHeight}
        onSelectionModelChange={handleSelectionChange}
      />
    </div>
    {data && data[select] &&
        <Button variant="contained" 
          className={classes.button}
          onClick={()=>{history.push(`/dataset/${data[select].id}`);}}
        >
          Edit Metadata
        </Button>
    }
    {data && data[select] &&
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
          {`API Code (Python) for dataset "${data[select].name}"`}
        </DialogTitle>
        <DialogContent>
          <GetDatasetPython dataset={data[select]} />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCodeClose} color="primary" autoFocus>
            Close 
          </Button>
        </DialogActions>
      </Dialog>
      </React.Fragment>
    }
    {data && data[select] &&
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
          {`API Code (MATLAB) for dataset "${data[select].name}"`}
        </DialogTitle>
        <DialogContent>
          <GetDatasetMatlab dataset={data[select]} />
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
