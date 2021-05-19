import React, { useEffect, useState } from "react";
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import Container from '@material-ui/core/Container';
import { useParams } from "react-router-dom";
import { 
  datasets
} from './Api'
import DatasetChart from './DatasetChart'

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    height: '100%',
  },
}));



export default function DatasetDetail() {
  const { id } = useParams();
  const classes = useStyles();

  const [dataset, setDataset] = useState(null)
  const [metadata, setMetadata] = useState(null)

  console.log('rendering with id', id);
  console.log('rendering with dataset', dataset);

  useEffect(() => {
    datasets(id).then((response) => {
      if (response.ok) {
        response.json().then(setDataset);
      }
    });
  }, []);

  if (dataset === null) {
    return (null);
  }

  return (
    <React.Fragment>
    <Container maxWidth="lg" className={classes.container}>
      <DatasetChart dataset={dataset} />
    </Container>
    <Container maxWidth="lg" className={classes.container}>
      <Paper>
      </Paper>
    </Container>
    </React.Fragment>
  );
}
