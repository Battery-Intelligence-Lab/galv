// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {SyntheticEvent, useState} from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import Connection, {APIMessage} from "./APIConnection";
import useStyles from "./UseStyles";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Snackbar from "@mui/material/Snackbar";

export default function UserProfile() {
  const { classes } = useStyles();
  const [email, setEmail] = useState<string>(Connection.user?.email || '')
  const [password, setPassword] = useState<string>('')
  const [currentPassword, setCurrentPassword] = useState<string>('')
  const [updateResult, setUpdateResult] = useState<APIMessage|null>()
  const [open, setOpen] = useState<boolean>(false)

  const updateUser = () => Connection.update_user(email, password, currentPassword)
    .then(setUpdateResult)
    .then(() => {
      setOpen(true)
      setEmail(Connection.user?.email || '')
      setPassword('')
      setCurrentPassword('')
    })

  const handleClose = (e: any, reason?: string) => {
    if (reason !== 'clickaway')
      setOpen(false)
  }

  return (
    <Container maxWidth="lg" className={classes.container} component="form">
      <Paper sx={{padding: 2}}>
        <Stack spacing={2}>
          <Typography variant="h5">{Connection.user?.username} profile</Typography>
          <TextField
            name="email"
            label="Email"
            value={email}
            InputProps={{
              classes: {
                input: classes.resize,
              },
            }}
            onChange={e => setEmail(e.target.value)}
          />
          <TextField
            name="password"
            label="Update password"
            type="password"
            helperText="Must be at least 8 characters"
            value={password}
            InputProps={{
              classes: {
                input: classes.resize,
              },
            }}
            onChange={e => setPassword(e.target.value)}
            error={password !== undefined && password.length > 0 && password.length < 8}
          />
          <TextField
            name="currentPassword"
            label="Current password"
            type="password"
            required
            value={currentPassword}
            InputProps={{
              classes: {
                input: classes.resize,
              },
            }}
            onChange={e => setCurrentPassword(e.target.value)}
          />
          <Button
            role="submit"
            fullWidth
            variant="contained"
            color="primary"
            onClick={updateUser}
          >
            Update profile
          </Button>
        </Stack>
        <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
          <Alert onClose={handleClose} severity={updateResult?.severity} sx={{ width: '100%' }}>
            {updateResult?.message}
          </Alert>
        </Snackbar>
      </Paper>
    </Container>
  );
}
