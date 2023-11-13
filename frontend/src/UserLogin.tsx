// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState, useCallback} from "react";
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Box from "@mui/material/Box";
import {useCurrentUser} from "./Components/CurrentUserContext";
import UseStyles from "./styles/UseStyles";
import Popover from "@mui/material/Popover";
import {ICONS, PATHS} from "./constants";
import Grid from "@mui/material/Unstable_Grid2";
import {Link} from "react-router-dom";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItem from "@mui/material/ListItem";
import List from "@mui/material/List";

export default function UserLogin() {
    const {user, login, logout, loginFormOpen, setLoginFormOpen} = useCurrentUser()
    const { classes } = UseStyles();

    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')

    // useState + useCallback to avoid child popover rendering with a null anchorEl
    const [popoverAnchorEl, setPopoverAnchorEl] = useState<HTMLElement|null>(null)
    const popoverAnchorRef = useCallback(
        (node: HTMLElement|null) => setPopoverAnchorEl(node),
        []
    )
    const do_login = () => {
        if (username === "" || password === "") return
        login(username, password)
        setLoginFormOpen(false)
    }

    const MainButton = user?
        <Button
            onClick={() => setLoginFormOpen(!loginFormOpen)}
            ref={popoverAnchorRef}
            startIcon={<ICONS.USER/>}
            variant="contained"
        >
            <Typography>{user.username}</Typography>
        </Button>
        : <Button
            onClick={() => setLoginFormOpen(true)}
            ref={popoverAnchorRef}
            variant="contained"
        >
            <Typography>Login</Typography>
        </Button>

    const popoverContent = user?
        <List>
            <ListItem>
                <ListItemIcon>
                    <ICONS.MANAGE_ACCOUNT />
                </ListItemIcon>
                <ListItemButton component={Link} to={`${PATHS.USER}/${user.id}?editing=true`}>
                    Manage Profile
                </ListItemButton>
            </ListItem>
            <ListItem>
                <ListItemIcon>
                    <ICONS.TOKEN />
                </ListItemIcon>
                <ListItemButton component={Link} to={`${PATHS.TOKEN}`}>
                    API Tokens
                </ListItemButton>
            </ListItem>
            <ListItem>
                <ListItemIcon>
                    <ICONS.LOGOUT />
                </ListItemIcon>
                <ListItemButton onClick={() => {
                    setUsername('')
                    setPassword('')
                    setLoginFormOpen(false)
                    logout()
                }}>
                    Logout
                </ListItemButton>
            </ListItem>
        </List>
        : <Box p={2}>
            <TextField
                autoFocus
                margin="dense"
                id="username"
                label="Username"
                type="text"
                fullWidth
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
                margin="dense"
                id="password"
                label="Password"
                type="password"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />
            <Button onClick={do_login} fullWidth={true}>Login</Button>
        </Box>

    return <Grid className={classes.userLoginBox} container>
        {popoverAnchorEl && <Popover
            open={loginFormOpen}
            onClose={() => setLoginFormOpen(false)}
            anchorEl={popoverAnchorEl}
            anchorOrigin={{vertical: 'bottom', horizontal: 'right'}}
            transformOrigin={{vertical: 'top', horizontal: 'right'}}
            onKeyDown={(e) => {
                if (!user && e.key === "Enter") {
                    do_login()
                }
            }}
        >
            {popoverContent}
        </Popover>}
        {MainButton}
    </Grid>
}
