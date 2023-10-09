// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

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
import ApproveUsers from "./ApproveUsers"
import Harvesters from "./Harvesters"
import Cells from "./Cells"
import Equipment from "./Equipment"
import Datasets from "./Datasets"
import HomeIcon from '@mui/icons-material/Home';
import PollIcon from '@mui/icons-material/Poll';
import DatasetLinkedIcon from '@mui/icons-material/DatasetLinked';
import MultilineChartIcon from '@mui/icons-material/MultilineChart';
import AssignmentIcon from '@mui/icons-material/Assignment';
import PrecisionManufacturingIcon from '@mui/icons-material/PrecisionManufacturing';
import BatteryFullIcon from '@mui/icons-material/BatteryFull';
import HolidayVillageIcon from '@mui/icons-material/HolidayVillage';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';
import { makeStyles} from "tss-react/mui";
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

import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import { ReactComponent as GalvLogo } from './Galv-logo.svg';
import Connection, {APIMessage} from "./APIConnection";
import Stack from "@mui/material/Stack";
import Tokens from "./Tokens";
import UserProfile from "./UserProfile";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";

const PrivateRoute = (component: JSX.Element) => {
  const logged = Connection.is_logged_in;

  return logged? component : <Navigate to='/login' />;
}

const drawerWidth = 240;
const useStyles = makeStyles()((theme) => {
  return {
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
      // ...theme.mixins.toolbar,
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
    galvLogo: {
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
      paddingTop: 20,
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
    appBarSpacer: {
      paddingTop: 44,
      //theme.mixins.toolbar,
    },
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
  }
});

export default function Core() {
  const { pathname } = useLocation();
  const { classes } = useStyles();
  console.log({classes})

  const userDisplayName = Connection.is_logged_in?  Connection.user?.username : ''

  const datasetsPath = "/"
  const isDatasetPath = matchPath({path: datasetsPath, end: true}, pathname) !== null
  const harvestersPath = "/harvesters"
  const isHarvestersPath = matchPath({path: harvestersPath, end: true}, pathname) !== null
  const cellsPath = "/cells"
  const isCellsPath = matchPath({path: cellsPath, end: true}, pathname) !== null
  const equipmentPath = "/equipment"
  const isEquipmentPath = matchPath({path: equipmentPath, end: true}, pathname) !== null
  const usersPath = "/users"
  const isUsersPath = matchPath({path: usersPath, end: true}, pathname) !== null
  const profilePath = "/profile"
  const tokenPath = "/tokens"

  const [open, setOpen] = React.useState(false);
  const handleDrawerOpen = () => {
    setOpen(true);
  };
  const handleDrawerClose = () => {
    setOpen(false);
  };

  const [snackbarOpen, setSnackbarOpen] = React.useState<boolean>(false)
  const [apiMessage, setAPIMessage] = React.useState<APIMessage|null>(null)
  const handleSnackbarClose = (e: any, reason?: string) => {
    if (reason !== 'clickaway') {
      setSnackbarOpen(false)
      setAPIMessage(null)
    }
  }
  Connection.message_handlers.push((h) => {
    setAPIMessage(h)
    setSnackbarOpen(true)
  })

  const mainListItems = (
    <Stack>
      <ListItemButton selected={isDatasetPath} component={Link} to={datasetsPath}>
        <ListItemIcon>
          <HomeIcon />
        </ListItemIcon>
        <ListItemText primary="Dashboard" />
      </ListItemButton>
      <Divider component="li" />
      <ListItemButton selected={isHarvestersPath} component={Link} to={harvestersPath}>
        <ListItemIcon>
          <DatasetLinkedIcon />
        </ListItemIcon>
        <ListItemText primary="Experiments" />
      </ListItemButton>
      <ListItemButton selected={isHarvestersPath} component={Link} to={harvestersPath}>
        <ListItemIcon>
          <MultilineChartIcon />
        </ListItemIcon>
        <ListItemText primary="Cycler Tests" />
      </ListItemButton>
      <Divider component="li" />
      <ListItemButton selected={isDatasetPath} component={Link} to={datasetsPath}>
        <ListItemIcon>
          <PollIcon />
        </ListItemIcon>
        <ListItemText primary="Datasets" />
      </ListItemButton>
      <ListItemButton selected={isCellsPath} component={Link} to={cellsPath}>
        <ListItemIcon>
          <BatteryFullIcon />
        </ListItemIcon>
        <ListItemText primary="Cells" />
      </ListItemButton>
      <ListItemButton selected={isEquipmentPath} component={Link} to={equipmentPath}>
        <ListItemIcon>
          <PrecisionManufacturingIcon/>
        </ListItemIcon>
        <ListItemText primary="Equipment" />
      </ListItemButton>
      <ListItemButton selected={isUsersPath} component={Link} to={usersPath}>
        <ListItemIcon>
          <AssignmentIcon/>
        </ListItemIcon>
        <ListItemText primary="Schedules" />
      </ListItemButton>
      <Divider component="li" />
      <ListItemButton selected={isUsersPath} component={Link} to={usersPath}>
        <ListItemIcon>
          <HolidayVillageIcon/>
        </ListItemIcon>
        <ListItemText primary="Labs" />
      </ListItemButton>
      <ListItemButton selected={isUsersPath} component={Link} to={usersPath}>
        <ListItemIcon>
          <PeopleAltIcon/>
        </ListItemIcon>
        <ListItemText primary="Teams" />
      </ListItemButton>
    </Stack>
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
          <GalvLogo className={classes.galvLogo}/>
          <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
          </Typography>

          <Button color="inherit" >
            User: {userDisplayName}
          </Button>
          <Button color="inherit" onClick={() => {
            navigate(profilePath)
          }}>
            Manage Profile
          </Button>
          <Button color="inherit" onClick={() => {
            navigate(tokenPath)
          }}>
            Manage API Tokens
          </Button>
          <Button color="inherit" onClick={() => {
            Connection.logout().then(()=> {navigate('/login');});
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
      <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
        <Alert onClose={handleSnackbarClose} severity={apiMessage?.severity} sx={{ width: '100%' }}>
          {apiMessage?.message}
        </Alert>
      </Snackbar>
    </div>
  );

  /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
  return (
    <Routes>
      <Route path="/login" element={<Login />}/>
      <Route path={datasetsPath} element={PrivateRoute(Layout)}>
        <Route path={cellsPath} element={Cells()} />
        <Route path={equipmentPath} element={Equipment()} />
        <Route path={harvestersPath} element={Harvesters()} />
        <Route path={usersPath} element={ApproveUsers()} />
        <Route path={profilePath} element={UserProfile()} />
        <Route path={tokenPath} element={Tokens()} />
        <Route index element={Datasets()} />
      </Route>
    </Routes>
  );
}
