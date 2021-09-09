import React, {useEffect} from "react";
import {
  Switch,
  Route,
  Redirect,
  Link,
  useHistory,
  useLocation,
  matchPath,
} from "react-router-dom";
import Login from "./Login"
import Harvesters from "./Harvesters"
import DatasetDetail from "./DatasetDetail"
import Cells from "./Cells"
import SpeedIcon from '@material-ui/icons/Speed';
import Equipment from "./Equipment"
import Datasets from "./Datasets"
import TableChartIcon from '@material-ui/icons/TableChart';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import BatteryUnknownIcon from '@material-ui/icons/BatteryUnknown';
import BackupIcon from '@material-ui/icons/Backup';
import {loggedIn, logout, getToken, getUser, isAdmin} from "./Api"
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
  const { pathname } = useLocation();
  const classes = useStyles();
  const [user, setUser] = React.useState(null);

  useEffect(() => {
    getUser().then(setUser)
  }, []);

  const handleLogin = () => {
    getUser().then(setUser)
  }

  const userIsAdmin = isAdmin()

  let userDisplayName = ''
  if (user) {
    userDisplayName = userIsAdmin ? 
      user.username + " (Admin)" :
      user.username
  }

  const datasetsPath = "/"
  const isDatasetPath = matchPath(pathname, 
    {path: datasetsPath, exact:true}
  )
  const harvestersPath = "/harvesters"
  const isHarvestersPath = matchPath(pathname, 
    {path: harvestersPath, exact:true}
  )
  const cellsPath = "/cells"
  const isCellsPath = matchPath(pathname, 
    {path: cellsPath, exact:true}
  )
  const equipmentPath = "/equipment"
  const isEquipmentPath = matchPath(pathname, 
    {path: equipmentPath, exact:true}
  )
  console.log('paths:', isDatasetPath, isHarvestersPath)


  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  const [tokenOpen, setTokenOpen] = React.useState(false);
  const [token, setToken] = React.useState();

  const handleTokenOpen = () => {
    getToken().then(response => response.json()).then(data => {
      setToken(data.access_token)
      setTokenOpen(true);
    });
  };

  const handleTokenClose = () => {
    setTokenOpen(false);
  };

  const tokenGenerator = (
    <React.Fragment>
    <Button color="inherit" onClick={handleTokenOpen}>
      Generate API token
    </Button>
    <Dialog
        open={tokenOpen}
        onClose={handleTokenClose}
      >
        <DialogTitle>
          {"API Token"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText style={{ wordWrap: 'break-word' }}>
            {token}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleTokenClose} color="primary" autoFocus>
            Close 
          </Button>
        </DialogActions>
      </Dialog>
    </React.Fragment>
  )

  const mainListItems = (
    <div>
      <ListItem button 
        selected={isDatasetPath} 
        component={Link} to={datasetsPath}>
        <ListItemIcon>
          <TableChartIcon />
        </ListItemIcon>
        <ListItemText primary="Datasets" />
      </ListItem>
      <ListItem button 
        selected={isHarvestersPath} 
        component={Link} to={harvestersPath}>
        <ListItemIcon>
          <BackupIcon />
        </ListItemIcon>
        <ListItemText primary="Harvesters" />
      </ListItem>
      <ListItem button 
        selected={isCellsPath} 
        component={Link} to={cellsPath}>
        <ListItemIcon>
          <BatteryUnknownIcon />
        </ListItemIcon>
        <ListItemText primary="Cells" />
      </ListItem>
      <ListItem button 
        selected={isEquipmentPath} 
        component={Link} to={equipmentPath}>
        <ListItemIcon>
          <SpeedIcon/>
        </ListItemIcon>
        <ListItemText primary="Equipment" />
      </ListItem>


    </div>
  );

  let history = useHistory();

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
        </Typography>

        <Button color="inherit" >
          User: {userDisplayName}
        </Button>
        {tokenGenerator}
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
          <Login onLogin={handleLogin}/>
        </Route>
        <Route>
          {logged_in}
        </Route>
    </Switch>
  );
}
 

