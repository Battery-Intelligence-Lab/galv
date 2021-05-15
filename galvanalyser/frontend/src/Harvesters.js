import React, { useEffect, useState } from "react";
import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Grid from '@material-ui/core/Grid';
import { harvester } from './Api';
import HarvesterSummary from './HarvesterSummary';


const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
}));

export default function Harvesters() {
  const classes = useStyles();
  const [harv, setHarv] = useState([])

  useEffect(() => {
    harvester().then((response) => {
      if (response.ok) {
        return response.json().then(setHarv);
      }
    });
  }, [])

  const harvester_render = harv.map((h) => {
    return (
      <Grid item xs={12} md={8} lg={9} key={h.machine_id}>
        <HarvesterSummary id={h.id} name={h.machine_id}/>
      </Grid>
    );
  });

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Grid container spacing={3}>
        { harvester_render }
      </Grid>
    </Container>
  );
}
