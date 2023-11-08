// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React from "react";
import {
  Routes,
  Route,
  Outlet,
  Link,
  useNavigate,
  useLocation,
  matchPath, useParams,
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
import {PATHS, ICONS, LookupKey, LOOKUP_KEYS} from "./constants";
import ErrorBoundary from "./Components/utils/ErrorBoundary";
import ResourceCard from "./Components/ResourceCard";
import FilterBar from "./Components/filtering/FilterBar";
import {FilterContextProvider} from "./Components/filtering/FilterContext";
import {ResourceList} from "./Components/ResourceList";

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
    content: {
      flexGrow: 1,
      height: '100vh',
      overflow: 'auto',
      paddingTop: theme.spacing(9),
      paddingLeft: theme.spacing(0),
      paddingRight: theme.spacing(0),
      paddingBottom: theme.spacing(0),
      fontFamily: 'Helvetica Neue,Helvetica,Arial,sans-serif',
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
          <FilterContextProvider>
            <FilterBar key="filter_bar" />
            <Outlet key="main_content" />
          </FilterContextProvider>
        </main>
        <Snackbar open={snackbarOpen} autoHideDuration={6000} onClose={handleSnackbarClose}>
          <Alert onClose={handleSnackbarClose} severity={apiMessage?.severity} sx={{ width: '100%' }}>
            {apiMessage?.message}
          </Alert>
        </Snackbar>
      </div>
  );

  function MyFallbackComponent(error: Error) {
    return (
        <div role="alert">
          <p>Something went wrong:</p>
          <pre>{error.message}</pre>
        </div>
    )
  }

  function get_lookup_key_from_pathname(pathname: string|undefined): LookupKey | undefined {
    return (
        (Object.entries(PATHS).find(([k, v]) => v === `/${pathname}`)?.[0] as keyof typeof PATHS)
    ) as LookupKey
  }

  function ResourceCardWrapper() {
    const navigate = useNavigate()
    const {type, id} = useParams()
    const lookup_key = get_lookup_key_from_pathname(type)
    console.log(`ResourceCardWrapper`, {type, id, lookup_key})
    if (!lookup_key || !id) {
      navigate(PATHS.DASHBOARD)
      return <></>
    }
    return <ResourceCard
        resource_id={id ?? -1}
        lookup_key={lookup_key ?? "CYCLER_TEST"}
        expanded={true}
    />
  }

  /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
  return <ErrorBoundary fallback={MyFallbackComponent}>
    <Routes>
      <Route path="/login" element={<Login />}/>
      <Route path={PATHS.DASHBOARD} element={Layout}>
        <Route path="/:type/:id" element={<ResourceCardWrapper/>}/>  {/* Handles direct resource lookups */}
        <Route path={PATHS.EXPERIMENT} element={<ResourceList lookup_key={LOOKUP_KEYS.EXPERIMENT}/>} />
        <Route path={PATHS.CYCLER_TEST} element={<ResourceList lookup_key={LOOKUP_KEYS.CYCLER_TEST}/>} />
        <Route path={PATHS.FILE} element={<ResourceList lookup_key={LOOKUP_KEYS.FILE}/>} />
        <Route path={PATHS.CELL} element={<ResourceList lookup_key={LOOKUP_KEYS.CELL}/>} />
        <Route path={PATHS.CELL_FAMILY} element={<ResourceList lookup_key={LOOKUP_KEYS.CELL_FAMILY}/>} />
        <Route path={PATHS.EQUIPMENT} element={<ResourceList lookup_key={LOOKUP_KEYS.EQUIPMENT}/>} />
        <Route path={PATHS.EQUIPMENT_FAMILY} element={<ResourceList lookup_key={LOOKUP_KEYS.EQUIPMENT_FAMILY}/>} />
        <Route path={PATHS.SCHEDULE} element={<ResourceList lookup_key={LOOKUP_KEYS.SCHEDULE}/>} />
        <Route path={PATHS.SCHEDULE_FAMILY} element={<ResourceList lookup_key={LOOKUP_KEYS.SCHEDULE_FAMILY}/>} />
        <Route path={PATHS.LAB} element={<ResourceList lookup_key={LOOKUP_KEYS.LAB}/>} />
        <Route path={PATHS.TEAM} element={<ResourceList lookup_key={LOOKUP_KEYS.TEAM}/>} />
        {/*<Route path={profilePath} element={UserProfile()} />*/}
        {/*<Route path={tokenPath} element={Tokens()} />*/}
        {/*<Route index element={Dashboard()} />*/}
        <Route index element={<ResourceList lookup_key={LOOKUP_KEYS.CYCLER_TEST}/>} />
      </Route>
    </Routes>
  </ErrorBoundary>
}
