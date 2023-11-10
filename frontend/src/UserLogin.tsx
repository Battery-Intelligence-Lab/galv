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
import {useNavigate} from "react-router-dom";

export default function UserLogin() {
    const {user, login, logout, loginFormOpen, setLoginFormOpen} = useCurrentUser()
    const navigate = useNavigate()
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

    if (user)
        return <Grid className={classes.userLoginBox} container >
            <Button onClick={() => setLoginFormOpen(!loginFormOpen)}>
                <ICONS.USER />
                <Typography>{user.username}</Typography>
            </Button>
            {loginFormOpen && <Grid container>
                <Button
                onClick={() => {
                    setLoginFormOpen(false)
                    navigate(`${PATHS.USER}/${user.id}?editing=true`)
                }}
            >
                Manage profile
            </Button>
                <Button
                onClick={() => {
                    setUsername('')
                    setPassword('')
                    setLoginFormOpen(false)
                    logout()
                }}
            >
                Logout
            </Button>
            </Grid>}
        </Grid>

    return <Grid className={classes.userLoginBox} container>
        {popoverAnchorEl && <Popover
            open={loginFormOpen}
            onClose={() => setLoginFormOpen(false)}
            anchorEl={popoverAnchorEl}
            anchorOrigin={{vertical: 'bottom', horizontal: 'center'}}
            onKeyDown={(e) => {
                if (e.key === "Enter") {
                    do_login()
                }
            }}
        >
            <Box p={2}>
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
                <Button onClick={do_login}>Login</Button>
            </Box>
        </Popover>}
        <Button onClick={() => setLoginFormOpen(true)} ref={popoverAnchorRef}>Login</Button>
    </Grid>
}
