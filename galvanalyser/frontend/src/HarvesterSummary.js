import { makeStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { Link } from "react-router-dom";


const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  bullet: {
    display: 'inline-block',
    margin: '0 2px',
    transform: 'scale(0.8)',
  },
  title: {
    fontSize: 14,
  },
  pos: {
    marginBottom: 12,
  },
}));

export default function HarvesterSummary(props) {
  const classes = useStyles();
  const id = props.id;
  const name = props.name;
  const harvester_url = `/harvester/${id}`;

  return (
    <Container maxWidth="lg" className={classes.container}>
    <Card className={classes.root} variant="outlined">
      <CardContent>
        <Typography className={classes.title} color="textSecondary" gutterBottom>
          {name} 
        </Typography>
        <Typography variant="body2" component="p">
          last run:
        </Typography>
      </CardContent>
      <CardActions>
      <Link to={harvester_url}>
        <Button size="small">Configure</Button>
      </Link>
      </CardActions>
    </Card>
    </Container>
  );
}
