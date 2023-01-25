import React from "react";
import {
  Routes,
  Route,
  Outlet,
  Navigate,
  Link,
  useNavigate,
  useLocation,
  matchPath,
} from "react-router-dom";
import Login from "./Login"
import Harvesters from "./Harvesters"
import DatasetDetail from "./DatasetDetail"
import Cells from "./Cells"
import SpeedIcon from '@mui/icons-material/Speed';
import Equipment from "./Equipment"
import Datasets from "./Datasets"
import TableChartIcon from '@mui/icons-material/TableChart';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import BatteryUnknownIcon from '@mui/icons-material/BatteryUnknown';
import BackupIcon from '@mui/icons-material/Backup';
import {loggedIn, handleLogin, logout, getToken, getUser, isAdmin} from "./Api"
import { makeStyles} from "@mui/styles";
import CssBaseline from '@mui/material/CssBaseline';

import clsx from 'clsx';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import Button from '@mui/material/Button';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { ReactComponent as GalvanalyserLogo } from './Galvanalyser-logo.svg';

const PrivateRoute = (component) => {
  const logged = loggedIn();

  return logged? component : <Navigate to='/login' />;
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



export default function Core() {
  const { pathname } = useLocation();
  const classes = useStyles();

  const user = getUser()

  const userIsAdmin = isAdmin()

  let userDisplayName = ''
  if (user) {
    userDisplayName = userIsAdmin ? 
      user.username + " (Admin)" :
      user.username
  }

  const datasetsPath = "/"
  const isDatasetPath = matchPath({path: datasetsPath, exact:true}, pathname) !== null
  const harvestersPath = "/harvesters"
  const isHarvestersPath = matchPath({path: harvestersPath, exact:true}, pathname) !== null
  const cellsPath = "/cells"
  const isCellsPath = matchPath({path: cellsPath, exact:true}, pathname) !== null
  const equipmentPath = "/equipment"
  const isEquipmentPath = matchPath({path: equipmentPath, exact:true}, pathname) !== null
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

  let navigate = useNavigate();

  const Layout = (
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
          logout().then(()=> {navigate('/login');});
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
        <Outlet />
    </main>
    </div>
  );

  /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
  return (
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin}/>}/>
        <Route path="/" element={PrivateRoute(Layout)}>
          <Route path="/cells" element={Cells()} />
          <Route path="/equipment" element={Equipment()} />
          <Route path="/harvesters" element={Harvesters()} />
          <Route path="/dataset/:id" element={DatasetDetail()} />
          <Route index element={Datasets()} />
        </Route>
      </Routes>
  );
}
 

