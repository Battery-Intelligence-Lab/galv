// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import { makeStyles } from 'tss-react/mui'
import React, {useState, useRef, FormEvent, Fragment} from "react";
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Alert from '@mui/material/Alert';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";
import {User} from "./api_codegen";
import {useCurrentUser} from "./Components/CurrentUserContext";
import {ReactSVG} from "react-svg";
import UseStyles from "./styles/UseStyles";


export default function Login() {
  const { classes } = UseStyles();
  const [createdUser, setCreatedUser] = useState<User|null>(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [registerMode, setRegisterMode] = useState<boolean>(false)

  const {login} = useCurrentUser()

  const submit = useRef<HTMLButtonElement>(null);
  const username_input = useRef<HTMLDivElement>(null);
  const password_input = useRef<HTMLDivElement>(null);
  const email_input = useRef<HTMLDivElement>(null);

  const handleEnterKey = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if(e.key === "Enter") {
      if (username === "") username_input.current?.focus();
      else if (password === "") password_input.current?.focus();
      else if (registerMode && email === "") email_input.current?.focus();
      else submit.current?.click();
    }
  }

  const onSubmitClick = (e: FormEvent)=>{
    e.preventDefault()
    if (username === "") username_input.current?.focus();
    else if (password === "") password_input.current?.focus();
    else if (registerMode && email === "") email_input.current?.focus();
    else {
      if (registerMode) {
        // TODO
        console.error("Register mode not implemented")
      } else
        login(username, password)
    }
  }

  const handleUsernameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUsername(e.target.value)
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value)
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
  }

  const createdUserContent = <Stack spacing={2}>
    <Typography component="h1" variant="h5">
      Success
    </Typography>
    <Typography>
      {`The user '${createdUser?.username}' has been created, but is currently inactive.`}
    </Typography>
    <Typography>
      New users need to be approved by an existing user before they are
      able to use the system.
    </Typography>
    <Typography>
      To approve a user, log in to Galv as an active user and
      select the appropriate unapproved user from the 'users' tab on the left.
    </Typography>
    <Button
        fullWidth
        variant="contained"
        color="primary"
        className={classes.submit}
        onClick={()=>window.location.reload()}
    >
      Log in with another account
    </Button>
  </Stack>

  const formContent = <Fragment>
    <Grid container sx={{width: '100%'}}>
      <Grid
          item
          sx={{width: '50%'}}
          className={!registerMode? classes.textActive : classes.textInactive}
          onClick={() => setRegisterMode(!registerMode)}
      >
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
      </Grid>
      <Grid
          item
          sx={{width: '50%'}}
          className={registerMode? classes.textActive : classes.textInactive}
          onClick={() => setRegisterMode(!registerMode)}
      >
        <Typography component="h1" variant="h5">
          Register
        </Typography>
      </Grid>
    </Grid>
    <form onSubmit={onSubmitClick}>
      <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          id="username"
          label="Username"
          name="username"
          autoComplete="username"
          onChange={handleUsernameChange}
          onKeyDown={handleEnterKey}
          ref={username_input}
          autoFocus
      />
      <TextField
          variant="outlined"
          margin="normal"
          required
          fullWidth
          name="password"
          label="Password"
          type="password"
          onChange={handlePasswordChange}
          onKeyDown={handleEnterKey}
          ref={password_input}
          id="password"
          autoComplete="current-password"
      />
      {registerMode && <Tooltip title="An email address is required in case you forget your password.">
        <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="email"
            label="Email address"
            type="email"
            onChange={handleEmailChange}
            onKeyDown={handleEnterKey}
            ref={email_input}
            id="email"
            autoComplete="email"
        />
      </Tooltip>}
      {error &&
          <Alert severity="error">
            {error}
          </Alert>
      }
      <Button
          type="submit"
          ref={submit}
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
      >
        {registerMode? 'Create new user' : 'Sign in'}
      </Button>
    </form>
    {registerMode && <Box>
      <Typography>
        New users will need to be approved by an existing user before they are
        able to use the system.
      </Typography>
      <Typography>
        To approve a user, log in to Galv and
        select the appropriate user from the 'users' tab on the left.
      </Typography>
    </Box>}
  </Fragment>

  return (
      <Container component="main" maxWidth="xs">
        <CssBaseline />
        <div className={classes.loginPaper}>
            <ReactSVG className={classes.galvLogo} src="Galv-logo.svg" />
          {createdUser !== null? createdUserContent : formContent}
        </div>
      </Container>
  )
}
