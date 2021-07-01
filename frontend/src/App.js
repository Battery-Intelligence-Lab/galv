import React from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Redirect,
  Link,
  useHistory,
  useLocation,
} from "react-router-dom";
import Login from "./Login"
import Harvesters from "./Harvesters"
import HarvesterDetail from "./HarvesterDetail"
import DatasetDetail from "./DatasetDetail"
import Cells from "./Cells"
import SpeedIcon from '@material-ui/icons/Speed';
import Equipment from "./Equipment"
import Datasets from "./Datasets"
import TableChartIcon from '@material-ui/icons/TableChart';
import BusinessIcon from '@material-ui/icons/Business';
import BatteryUnknownIcon from '@material-ui/icons/BatteryUnknown';
import BackupIcon from '@material-ui/icons/Backup';
import {loggedIn, logout} from "./Api"
import { makeStyles } from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';

import clsx from 'clsx';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Button from '@material-ui/core/Button';
import MenuIcon from '@material-ui/icons/Menu';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';

import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import DashboardIcon from '@material-ui/icons/Dashboard';
import ShoppingCartIcon from '@material-ui/icons/ShoppingCart';
import { ReactComponent as GalvanalyserLogo } from './Galvanalyser-logo.svg';




const PrivateRoute = ({ component: Component, ...rest }) => {
  const logged = loggedIn();

  return <Route {...rest} render={(props) => (
    logged
      ? <Component {...props} />
      : <Redirect to='/login' />
  )} />
}

const drawerWidth = 240;

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  toolbar: {
    paddingRight: 24, // keep right padding when drawer closed
  },
  toolbarIcon: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: '0 8px',
    ...theme.mixins.toolbar,
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
  },
  appBarShift: {
    marginLeft: drawerWidth,
    width: `calc(100% - ${drawerWidth}px)`,
    transition: theme.transitions.create(['width', 'margin'], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  galvanalyserLogo: {
    height: '40px' 
  },
  menuButton: {
    marginRight: 36,
  },
  menuButtonHidden: {
    display: 'none',
  },
  title: {
    marginLeft: 16,
    flexGrow: 1,
  },
  drawerPaper: {
    position: 'relative',
    whiteSpace: 'nowrap',
    width: drawerWidth,
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.enteringScreen,
    }),
  },
  drawerPaperClose: {
    overflowX: 'hidden',
    transition: theme.transitions.create('width', {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen,
    }),
    width: theme.spacing(7),
    [theme.breakpoints.up('sm')]: {
      width: theme.spacing(9),
    },
  },
  appBarSpacer: theme.mixins.toolbar,
  content: {
    flexGrow: 1,
    height: '100vh',
    overflow: 'auto',
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: 'flex',
    overflow: 'auto',
    flexDirection: 'column',
  },
  fixedHeight: {
    height: 240,
  },
}));



export default function App() {
  const classes = useStyles();
  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  const mainListItems = (
    <div>
      <ListItem button component={Link} to="/">
        <ListItemIcon>
          <TableChartIcon />
        </ListItemIcon>
        <ListItemText primary="Datasets" />
      </ListItem>
      <ListItem button component={Link} to="/harvesters">
        <ListItemIcon>
          <BackupIcon />
        </ListItemIcon>
        <ListItemText primary="Harvesters" />
      </ListItem>
      <ListItem button component={Link} to="/cells">
        <ListItemIcon>
          <BatteryUnknownIcon />
        </ListItemIcon>
        <ListItemText primary="Cells" />
      </ListItem>
      <ListItem button component={Link} to="/equipment">
        <ListItemIcon>
          <SpeedIcon/>
        </ListItemIcon>
        <ListItemText primary="Equipment" />
      </ListItem>


    </div>
  );

  let history = useHistory();

  const location = useLocation();

  const logged_in = (
    <div className={classes.root}>
    <CssBaseline />
    <AppBar position="absolute" className={clsx(classes.appBar, open && classes.appBarShift)}>
      <Toolbar className={classes.toolbar}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="open drawer"
          onClick={handleDrawerOpen}
          className={clsx(classes.menuButton, open && classes.menuButtonHidden)}
        >
          <MenuIcon />
        </IconButton>
        <GalvanalyserLogo className={classes.galvanalyserLogo}/>
        <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
          - {location.pathname}
        </Typography>
        <Button color="inherit" onClick={() => {
          logout().then(()=> {history.push('/login');});
        }}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
    <Drawer
      variant="permanent"
      classes={{
        paper: clsx(classes.drawerPaper, !open && classes.drawerPaperClose),
      }}
      open={open}
    >
      <div className={classes.toolbarIcon}>
        <IconButton onClick={handleDrawerClose}>
          <ChevronLeftIcon />
        </IconButton>
      </div>
      <Divider />
      <List>{mainListItems}</List>
    </Drawer>
    <main className={classes.content}>
      <div className={classes.appBarSpacer} />
        {/* A <Switch> looks through its children <Route>s and
              renders the first one that matches the current URL. */}
        <Switch>
          <PrivateRoute path="/cells" component={Cells} />
          <PrivateRoute path="/equipment" component={Equipment} />
          <PrivateRoute path="/harvesters" component={Harvesters} />
          <PrivateRoute path="/dataset/:id" component={DatasetDetail} />
          <PrivateRoute path="/" component={Datasets} />
        </Switch>
    </main>
    </div>
  );


  return (
      <Switch>
        <Route path="/login">
          <Login />
        </Route>
        <Route>
          {logged_in}
        </Route>
    </Switch>
  );
}
 

