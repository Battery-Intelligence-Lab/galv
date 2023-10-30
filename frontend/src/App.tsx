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
import CyclerTestPage from "./Components/cycler-test/CyclerTestPage";
import CellList from "./Components/cell/CellList";
import CellPage from "./Components/cell/CellPage";
import CellFamilyCard from "./Components/cell/CellFamilyCard";
import ScheduleFamilyCard from "./Components/schedule/ScheduleFamilyCard";
import EquipmentFamilyCard from "./Components/equipment/EquipmentFamilyCard";
import {PATHS, ICONS} from "./constants";
import {ErrorBoundary} from "react-error-boundary";

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
        <ListItemButton selected={pathIs(PATHS.EXPERIMENT)} component={Link} to={PATHS.EXPERIMENT}>
          <ListItemIcon>
            <ICONS.EXPERIMENT />
          </ListItemIcon>
          <ListItemText primary="Experiments" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.CYCLER_TEST)} component={Link} to={PATHS.CYCLER_TEST}>
          <ListItemIcon>
            <ICONS.CYCLER_TEST />
          </ListItemIcon>
          <ListItemText primary="Cycler Tests" />
        </ListItemButton>
        <Divider component="li" />
        <ListItemButton selected={pathIs(PATHS.FILE)} component={Link} to={PATHS.FILE}>
          <ListItemIcon>
            <ICONS.FILE />
          </ListItemIcon>
          <ListItemText primary="Datasets" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.CELL)} component={Link} to={PATHS.CELL}>
          <ListItemIcon>
            <ICONS.CELL />
          </ListItemIcon>
          <ListItemText primary="Cells" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.EQUIPMENT)} component={Link} to={PATHS.EQUIPMENT}>
          <ListItemIcon>
            <ICONS.EQUIPMENT/>
          </ListItemIcon>
          <ListItemText primary="Equipment" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.SCHEDULE)} component={Link} to={PATHS.SCHEDULE}>
          <ListItemIcon>
            <ICONS.SCHEDULE/>
          </ListItemIcon>
          <ListItemText primary="Schedules" />
        </ListItemButton>
        <Divider component="li" />
        <ListItemButton selected={pathIs(PATHS.LAB)} component={Link} to={PATHS.LAB}>
          <ListItemIcon>
            <ICONS.LAB/>
          </ListItemIcon>
          <ListItemText primary="Labs" />
        </ListItemButton>
        <ListItemButton selected={pathIs(PATHS.TEAM)} component={Link} to={PATHS.TEAM}>
          <ListItemIcon>
            <ICONS.TEAM/>
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
              navigate(PATHS.TOKEN)
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

  function MyFallbackComponent({ error, resetErrorBoundary }: { error: Error, resetErrorBoundary: () => void}) {
    return (
        <div role="alert">
          <p>Something went wrong:</p>
          <pre>{error.message}</pre>
          <button onClick={resetErrorBoundary}>Try again</button>
        </div>
    )
  }

  /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
  return (
      <ErrorBoundary
          FallbackComponent={MyFallbackComponent}
          onError={(error, stack) => {
            console.error(error)
            console.info(stack)
          }}
      >
        <Routes>
          <Route path="/login" element={<Login />}/>
          <Route path={PATHS.DASHBOARD} element={Layout}>
            <Route path={PATHS.EXPERIMENT} element={<Experiments/>} />
            <Route path={`${PATHS.EXPERIMENT}/:uuid`} element={<Experiments/>} />
            <Route path={PATHS.CYCLER_TEST} element={<CyclerTestList/>} />
            <Route path={`${PATHS.CYCLER_TEST}/:uuid`} element={<CyclerTestPage/>} />
            <Route path={PATHS.DATASET} element={<>TODO</>} />
            <Route path={PATHS.CELL} element={<CellList/>} />
            <Route path={`${PATHS.CELL}/:uuid`} element={<CellPage />} />
            <Route path={PATHS.CELL_FAMILY} element={<>TODO</>} />
            <Route path={`${PATHS.CELL_FAMILY}/:uuid`} element={<CellFamilyCard />} />
            <Route path={PATHS.EQUIPMENT} element={<>TODO</>} />
            <Route path={`${PATHS.EQUIPMENT}/:uuid`} element={<>TODO</>} />
            <Route path={PATHS.EQUIPMENT_FAMILY} element={<>TODO</>} />
            <Route path={`${PATHS.EQUIPMENT_FAMILY}/:uuid`} element={<EquipmentFamilyCard />} />
            <Route path={PATHS.SCHEDULE} element={<>TODO</>} />
            <Route path={`${PATHS.SCHEDULE}/:uuid`} element={<>TODO</>} />
            <Route path={PATHS.SCHEDULE_FAMILY} element={<>TODO</>} />
            <Route path={`${PATHS.SCHEDULE_FAMILY}/:uuid`} element={<ScheduleFamilyCard />} />
            <Route path={PATHS.LAB} element={<>TODO</>} />
            <Route path={`${PATHS.LAB}/:uuid`} element={<>TODO</>} />
            <Route path={PATHS.TEAM} element={<>TODO</>} />
            <Route path={`${PATHS.TEAM}/:uuid`} element={<>TODO</>} />
            {/*<Route path={profilePath} element={UserProfile()} />*/}
            {/*<Route path={tokenPath} element={Tokens()} />*/}
            {/*<Route index element={Dashboard()} />*/}
            <Route index element={<CyclerTestList/>} />
          </Route>
        </Routes>
      </ErrorBoundary>
  );
}
