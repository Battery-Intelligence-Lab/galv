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
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import axios, {AxiosError} from "axios";
import Experiments from "./Experiments";
import CyclerTestList from "./Components/cycler-test/CyclerTestList";
import { ICONS } from "./icons";
import CyclerTestPage from "./Components/cycler-test/CyclerTestPage";
import CellList from "./Components/cell/CellList";
import CellPage from "./Components/cell/CellPage";
import CellFamilyCard from "./Components/cell/CellFamilyCard";
import ScheduleFamilyCard from "./Components/schedule/ScheduleFamilyCard";
import EquipmentFamilyCard from "./Components/equipment/EquipmentFamilyCard";

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

export const PATHS = {
  FILES: "/files",
  DASHBOARD: "/",
  EXPERIMENTS: "/experiments",
  CYCLER_TESTS: "/cycler_tests",
  DATASETS: "/datasets",
  CELLS: "/cells",
  CELL_FAMILIES: "/cell_families",
  EQUIPMENT: "/equipment",
  EQUIPMENT_FAMILIES: "/equipment_families",
  SCHEDULES: "/schedules",
  SCHEDULE_FAMILIES: "/schedule_families",
  LABS: "/labs",
  TEAMS: "/teams",
  USERS: "/users",
  PROFILE: "/profile",
  TOKENS: "/tokens",
}
export const pathMatches = (path: string, pathname: string) => matchPath({path: path, end: true}, pathname) !== null

export default function Core() {
  const { pathname } = useLocation();
  const pathIs = (path: string) => pathMatches(path, pathname)

  const { classes } = useStyles();

  const userDisplayName = Connection.is_logged_in?  Connection.user?.username : ''

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
  axios.interceptors.response.use(null, function (error: AxiosError) {
    // Suppress 401 errors and void login
    if (error.response?.status === 401) {
      window.localStorage.removeItem('user')
      axios.defaults.headers.common['Authorization'] = ''
      return Promise.reject(error)
    }

    setAPIMessage({message: error.response?.statusText || 'Error', severity: 'error'})
    setSnackbarOpen(true)
  });

  const mainListItems = (
      <Stack>
        <ListItemButton selected={pathIs(PATHS.DASHBOARD)} component={Link} to={PATHS.DASHBOARD}>
          <ListItemIcon>
            <ICONS.DASHBOARD />
          </ListItemIcon>
          <ListItemText primary="Dashboard" />
        </ListItemButton>
        <Divider component="li" />
        <ListItemButton selected={pathIs(PATHS.EXPERIMENTS)} component={Link} to={PATHS.EXPERIMENTS}>
          <ListItemIcon>
            <ICONS.EXPERIMENTS />
          </ListItemIcon>
          <ListItemText primary="Experiments" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.CYCLER_TESTS)} component={Link} to={PATHS.CYCLER_TESTS}>
          <ListItemIcon>
            <ICONS.CYCLER_TESTS />
          </ListItemIcon>
          <ListItemText primary="Cycler Tests" />
        </ListItemButton>
        <Divider component="li" />
        <ListItemButton selected={pathIs(PATHS.DATASETS)} component={Link} to={PATHS.DATASETS}>
          <ListItemIcon>
            <ICONS.DATASETS />
          </ListItemIcon>
          <ListItemText primary="Datasets" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.CELLS)} component={Link} to={PATHS.CELLS}>
          <ListItemIcon>
            <ICONS.CELLS />
          </ListItemIcon>
          <ListItemText primary="Cells" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.EQUIPMENT)} component={Link} to={PATHS.EQUIPMENT}>
          <ListItemIcon>
            <ICONS.EQUIPMENT/>
          </ListItemIcon>
          <ListItemText primary="Equipment" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.SCHEDULES)} component={Link} to={PATHS.SCHEDULES}>
          <ListItemIcon>
            <ICONS.SCHEDULES/>
          </ListItemIcon>
          <ListItemText primary="Schedules" />
        </ListItemButton>
        <Divider component="li" />
        <ListItemButton selected={pathIs(PATHS.LABS)} component={Link} to={PATHS.LABS}>
          <ListItemIcon>
            <ICONS.LABS/>
          </ListItemIcon>
          <ListItemText primary="Labs" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.TEAMS)} component={Link} to={PATHS.TEAMS}>
          <ListItemIcon>
            <ICONS.TEAMS/>
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
              navigate(PATHS.PROFILE)
            }}>
              Manage Profile
            </Button>
            <Button color="inherit" onClick={() => {
              navigate(PATHS.TOKENS)
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
        <Route path={PATHS.DASHBOARD} element={Layout}>
          <Route path={PATHS.EXPERIMENTS} element={<Experiments/>} />
          <Route path={`${PATHS.EXPERIMENTS}/:uuid`} element={<Experiments/>} />
          <Route path={PATHS.CYCLER_TESTS} element={<CyclerTestList/>} />
          <Route path={`${PATHS.CYCLER_TESTS}/:uuid`} element={<CyclerTestPage/>} />
          <Route path={PATHS.DATASETS} element={<>TODO</>} />
          <Route path={PATHS.CELLS} element={<CellList/>} />
          <Route path={`${PATHS.CELLS}/:uuid`} element={<CellPage />} />
          <Route path={PATHS.CELL_FAMILIES} element={<>TODO</>} />
          <Route path={`${PATHS.CELL_FAMILIES}/:uuid`} element={<CellFamilyCard />} />
          <Route path={PATHS.EQUIPMENT} element={<>TODO</>} />
          <Route path={`${PATHS.EQUIPMENT}/:uuid`} element={<>TODO</>} />
          <Route path={PATHS.EQUIPMENT_FAMILIES} element={<>TODO</>} />
          <Route path={`${PATHS.EQUIPMENT_FAMILIES}/:uuid`} element={<EquipmentFamilyCard />} />
          <Route path={PATHS.SCHEDULES} element={<>TODO</>} />
          <Route path={`${PATHS.SCHEDULES}/:uuid`} element={<>TODO</>} />
          <Route path={PATHS.SCHEDULE_FAMILIES} element={<>TODO</>} />
          <Route path={`${PATHS.SCHEDULE_FAMILIES}/:uuid`} element={<ScheduleFamilyCard />} />
          <Route path={PATHS.LABS} element={<>TODO</>} />
          <Route path={`${PATHS.LABS}/:uuid`} element={<>TODO</>} />
          <Route path={PATHS.TEAMS} element={<>TODO</>} />
          <Route path={`${PATHS.TEAMS}/:uuid`} element={<>TODO</>} />
          {/*<Route path={profilePath} element={UserProfile()} />*/}
          {/*<Route path={tokenPath} element={Tokens()} />*/}
          {/*<Route index element={Dashboard()} />*/}
          <Route index element={<CyclerTestList/>} />
        </Route>
      </Routes>
  );
}
