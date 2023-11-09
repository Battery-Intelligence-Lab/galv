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
import Button from '@mui/material/Button';
import MenuIcon from '@mui/icons-material/Menu';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';

import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import {ReactSVG} from 'react-svg';
import Stack from "@mui/material/Stack";
import {PATHS, ICONS, LookupKey, LOOKUP_KEYS} from "./constants";
import ErrorBoundary from "./Components/ErrorBoundary";
import ResourceCard from "./Components/ResourceCard";
import FilterBar from "./Components/filtering/FilterBar";
import {FilterContextProvider} from "./Components/filtering/FilterContext";
import {ResourceList} from "./Components/ResourceList";
import CurrentUserContextProvider from "./Components/CurrentUserContext";
import useStyles from "./styles/UseStyles";
import {SnackbarMessenger, SnackbarMessengerContextProvider} from "./Components/SnackbarMessengerContext";

export const pathMatches = (path: string, pathname: string) => matchPath({path: path, end: true}, pathname) !== null

export function Core() {
    const { pathname } = useLocation();
    const pathIs = (path: string) => pathMatches(path, pathname)

    const { classes } = useStyles();

    const [open, setOpen] = React.useState(false);
    const handleDrawerOpen = () => {
        setOpen(true);
    };
    const handleDrawerClose = () => {
        setOpen(false);
    };

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
            <ListItemButton selected={pathIs(PATHS.HARVESTER)} component={Link} to={PATHS.HARVESTER}>
                <ListItemIcon>
                    <ICONS.HARVESTER/>
                </ListItemIcon>
                <ListItemText primary="Harvesters" />
            </ListItemButton>
            <ListItemButton selected={pathIs(PATHS.PATH)} component={Link} to={PATHS.PATH}>
                <ListItemIcon>
                    <ICONS.PATH/>
                </ListItemIcon>
                <ListItemText primary="Paths" />
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
                    <ReactSVG className={classes.galvLogo} src="Galv-logo.svg" />
                    <Typography component="h1" variant="h6" color="inherit" noWrap className={classes.title}>
                    </Typography>

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
        const lookup_key = get_lookup_key_from_pathname(type)

        if (!lookup_key || !id) {
            navigate(PATHS.DASHBOARD)
            return <></>
        }

        return <ResourceCard
            resource_id={id ?? -1}
            lookup_key={lookup_key ?? "CYCLER_TEST"}
            expanded={true}
            sx={{margin: (t) => t.spacing(1)}}
        />
    }

    /* A <Routes> looks through its children <Route>s and renders the first one that matches the current URL. */
    return <ErrorBoundary fallback={MyFallbackComponent}>
        <Routes>
            <Route path="/login" element={<UserLogin />}/>
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
                <Route path={PATHS.HARVESTER} element={<ResourceList lookup_key={LOOKUP_KEYS.HARVESTER}/>} />
                <Route path={PATHS.PATH} element={<ResourceList lookup_key={LOOKUP_KEYS.PATH}/>} />
                <Route path={PATHS.LAB} element={<ResourceList lookup_key={LOOKUP_KEYS.LAB}/>} />
                <Route path={PATHS.TEAM} element={<ResourceList lookup_key={LOOKUP_KEYS.TEAM}/>} />
                {/*<Route path={profilePath} element={UserProfile()} />*/}
                <Route path={PATHS.TOKEN} element={<ResourceList lookup_key={LOOKUP_KEYS.TOKEN}/>} />
                {/*<Route index element={Dashboard()} />*/}
                <Route index element={<ResourceList lookup_key={LOOKUP_KEYS.CYCLER_TEST}/>} />
            </Route>
        </Routes>
    </ErrorBoundary>
}

export default function WrappedCore() {
    return <SnackbarMessengerContextProvider>
        <CurrentUserContextProvider>
            <Core />
        </CurrentUserContextProvider>
    </SnackbarMessengerContextProvider>
}
