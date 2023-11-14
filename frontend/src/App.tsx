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
    matchPath, useParams, useSearchParams,
} from "react-router-dom";
import UserLogin from "./UserLogin"
import CssBaseline from '@mui/material/CssBaseline';

import clsx from 'clsx';
import Drawer from '@mui/material/Drawer';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import List from '@mui/material/List';
import Typography from '@mui/material/Typography';
import Divider from '@mui/material/Divider';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import {ReactSVG} from 'react-svg';
import Stack from "@mui/material/Stack";
import {PATHS, ICONS, LookupKey, LOOKUP_KEYS, DISPLAY_NAMES_PLURAL} from "./constants";
import ErrorBoundary from "./Components/ErrorBoundary";
import ResourceCard from "./Components/ResourceCard";
import FilterBar from "./Components/filtering/FilterBar";
import {FilterContextProvider} from "./Components/filtering/FilterContext";
import {ResourceList} from "./Components/ResourceList";
import CurrentUserContextProvider from "./Components/CurrentUserContext";
import useStyles from "./styles/UseStyles";
import {SnackbarMessenger, SnackbarMessengerContextProvider} from "./Components/SnackbarMessengerContext";
import Tooltip from "@mui/material/Tooltip";
import LookupKeyIcon from "./Components/LookupKeyIcon";
import Dashboard from "./Dashboard";

export const pathMatches = (path: string, pathname: string) => matchPath({path: path, end: true}, pathname) !== null

export function Core() {
    const { pathname } = useLocation();
    const pathIs = (path: string) => pathMatches(path, pathname)

    const { classes } = useStyles();

    const [open, setOpen] = React.useState(false);
    const toggleDrawerOpen = () => {
        setOpen(!open);
    };
    const handleDrawerClose = () => {
        setOpen(false);
    };

    const LI = ({lookupKey}: { lookupKey: LookupKey }) => <ListItemButton
        selected={pathIs(PATHS[lookupKey])}
        component={Link}
        to={PATHS[lookupKey]}
        key={lookupKey}
    >
        <ListItemIcon key="icon">
            <LookupKeyIcon lookupKey={lookupKey} tooltip={!open} tooltipProps={{placement: "right"}} />
        </ListItemIcon>
        <ListItemText key="text" primary={DISPLAY_NAMES_PLURAL[lookupKey]} />
    </ListItemButton>

    const mainListItems = (
        <Stack>
            <ListItemButton key="dashboard" selected={pathIs(PATHS.DASHBOARD)} component={Link} to={PATHS.DASHBOARD}>
                <ListItemIcon>
                    <ICONS.DASHBOARD />
                </ListItemIcon>
                <ListItemText primary="Dashboard" />
            </ListItemButton>
            <Divider component="li" key="div0" />
            {[LOOKUP_KEYS.EXPERIMENT, LOOKUP_KEYS.CYCLER_TEST].map(lookupKey => <LI key={lookupKey} lookupKey={lookupKey} />)}
            <Divider component="li" key="div1" />
            {[
                LOOKUP_KEYS.FILE,
                LOOKUP_KEYS.CELL,
                LOOKUP_KEYS.EQUIPMENT,
                LOOKUP_KEYS.SCHEDULE,
            ].map(lookupKey => <LI key={lookupKey} lookupKey={lookupKey} />)}
            <Divider component="li" key="div2" />
            {[
                LOOKUP_KEYS.HARVESTER,
                LOOKUP_KEYS.PATH,
                LOOKUP_KEYS.VALIDATION_SCHEMA,
            ].map(lookupKey => <LI key={lookupKey} lookupKey={lookupKey} />)}
            <Divider component="li" key="div3" />
            {[
                LOOKUP_KEYS.LAB,
                LOOKUP_KEYS.TEAM,
            ].map(lookupKey => <LI key={lookupKey} lookupKey={lookupKey} />)}
        </Stack>
    );

    const Layout = (
        <div className={classes.root}>
            <CssBaseline />
            <AppBar position="absolute" className={clsx(classes.appBar, open && classes.appBarShift)}>
                <Toolbar className={classes.toolbar}>
                    <IconButton
                        edge="start"
                        color="inherit"
                        aria-label="open drawer"
                        onClick={toggleDrawerOpen}
                        className={clsx(classes.menuButton)}
                    >
                        <MenuIcon />
                    </IconButton>
                    <Link to={PATHS.DASHBOARD} className={classes.title}>
                        <Tooltip title="Galv" describeChild={true} placement="bottom-start" arrow>
                            <div>
                                <ReactSVG className={classes.galvLogo} src="/Galv-logo.svg" />
                            </div>
                        </Tooltip>
                    </Link>
                    <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
                        The Battery Development Metadata Secretary
                    </Typography>
                    <UserLogin />
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
            <SnackbarMessenger autoHideDuration={6000} />
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
        const [searchParams] = useSearchParams();
        const lookup_key = get_lookup_key_from_pathname(type)

        if (!lookup_key || !id) {
            navigate(PATHS.DASHBOARD)
            return <></>
        }

        return <ResourceCard
            resource_id={id ?? -1}
            lookup_key={lookup_key ?? "CYCLER_TEST"}
            expanded={true}
            editing={searchParams.get('editing') === 'true'}
            sx={{margin: (t) => t.spacing(1)}}
        />
    }

    function ResourceListWrapper() {
        const navigate = useNavigate()
        const {type} = useParams()
        const lookup_key = get_lookup_key_from_pathname(type)

        if (!lookup_key) {
            navigate(PATHS.DASHBOARD)
            return <></>
        }

        return <ResourceList lookup_key={lookup_key ?? "CYCLER_TEST"}/>
    }

    /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
    return <ErrorBoundary fallback={MyFallbackComponent}>
        <Routes>
            <Route path={PATHS.DASHBOARD} element={Layout}>
                {/*<Route path={PATHS.GRAPH} element={<DatasetChart />} />*/}
                <Route path="/:type/:id" element={<ResourceCardWrapper/>}/>  {/* Handles direct resource lookups */}
                <Route path={"/:type"} element={<ResourceListWrapper/>}/>  {/* Handles resource lists */}
                <Route index element={<Dashboard key="dashboard" />} />
            </Route>
        </Routes>
    </ErrorBoundary>
}

export default function WrappedCore() {
    // CurrentUserContextProvider relies on SnackbarMessengerContextProvider to alert when
    // the user is logged out by the server
    return <SnackbarMessengerContextProvider>
        <CurrentUserContextProvider>
            <Core />
        </CurrentUserContextProvider>
    </SnackbarMessengerContextProvider>
}
