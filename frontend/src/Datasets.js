
import React, {useEffect, useState, useRef} from "react";
import { DataGrid, GridRowsProp, GridColDef } from '@material-ui/data-grid';
import Container from '@material-ui/core/Container';
import { datasets, users, cells } from './Api';
import { makeStyles } from '@material-ui/core/styles';
import DatasetChart from './DatasetChart'
import Button from '@material-ui/core/Button';
import { useHistory } from "react-router-dom";

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    height: '100%',
  },
}));



export default function Datasets() {
  const [data, setData] = useState([])
  const classes = useStyles();
  const history = useHistory();

  const [select, setSelect] = useState(null)

  const handleSelectionChange = (e) => {
    setSelect(e.selectionModel[0]);
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

  if ( !data ) {
    return ("Loading...");
  }
  const columns: GridColDef[] = [
    { field: 'dataset_id', headerName: 'ID', width: 70},
    { field: 'name', headerName: 'Name', flex: true},
    { 
      field: 'date', headerName: 'Date', width: 110,
      valueFormatter: (params: GridValueFormatterParams) => {
        return Intl.DateTimeFormat('en-GB').format(params.value);
      }
    },
    { field: 'dataset_type', headerName: 'Type', width: 90 },
    { field: 'cell', headerName: 'Cell', width: 100 },
    { field: 'owner', headerName: 'Owner', width: 120 },
    { field: 'purpose', headerName: 'Purpose', width: 250 },
    { field: 'metadata', headerName: 'Metadata', type: 'boolean', width: 120 },
  ];

  const rows: GridRowsProp = data.map((d, i) => {
    return {
      id: i,
      dataset_id: d.id,
      name: d.name,
      dataset_type: d.dataset_type,
      date: Date.parse(d.date),
      cell: d.cell ? d.cell.name : '',
      owner: d.owner ? d.owner.username : '',
      purpose: d.purpose,
      metadata: !(!d.cell || !d.owner || !d.purpose || !d.equipment)
    };
  });

  

  let autoHeight = true;
  let divStyle = { width: '100%' };
  

  return (
    <Container maxWidth="lg" className={classes.container}>
      <div style={divStyle}>
      <DataGrid 
        rows={rows} columns={columns} 
        density='compact'
        autoPageSize
        loading={rows.length === 0}
        rowHeight={38}
        autoHeight={autoHeight}
        onSelectionModelChange={handleSelectionChange}
      />
    </div>
    {data[select] &&
        <Button variant="contained" 
          onClick={()=>{history.push(`/dataset/${data[select].id}`);}}
        >
          Edit Metadata
        </Button>
    }
    </Container>
  );
}
