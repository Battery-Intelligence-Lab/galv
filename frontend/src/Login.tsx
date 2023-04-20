// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import { makeStyles } from '@mui/styles'
import React, {useState, useRef, FormEvent, Fragment} from "react";
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Alert from '@mui/material/Alert';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { useNavigate } from "react-router-dom";
import { ReactComponent as GalvanalyserIcon} from './Galvanalyser-icon.svg';
import Connection, {User} from "./APIConnection";
import Grid from "@mui/material/Grid";
import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Tooltip from "@mui/material/Tooltip";

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  icon: {
    margin: theme.spacing(1),
    width: theme.spacing(7),
    height: theme.spacing(10),
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  textActive: {
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.common.white,
    textAlign: 'center',
    cursor: 'pointer',
  },
  textInactive: {
    textAlign: 'center',
    cursor: 'pointer',
  }
}));


export default function Login() {
  const classes = useStyles();
  const [createdUser, setCreatedUser] = useState<User|null>(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [registerMode, setRegisterMode] = useState<boolean>(false)

  const navigate = useNavigate();

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
    console.log("You pressed login")
    if (username === "") username_input.current?.focus();
    else if (password === "") password_input.current?.focus();
    else if (registerMode && email === "") email_input.current?.focus();
    else {
      if (registerMode) {
        Connection.create_user(username, email, password)
          .then(user => {console.log('new user', user); return user})
          .then(user => setCreatedUser(user))
          .catch(e => setError(e.message))
      } else
        Connection.login(username, password).then(ok => {
          if (!ok) {
            setError('Unable to log in');
          } else {
            setError('')
            navigate('/');
          }
        });
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
      New users need to be activated by an existing user before they are
      able to use the system.
    </Typography>
    <Typography>
      To activate a user, log in to Galvanalyser as an active user and
      select the appropriate inactive user from the 'users' tab on the left.
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
            New users will need to be activated by an existing user before they are
            able to use the system.
        </Typography>
        <Typography>
            To activate a user, log in to Galvanalyser and
            select the appropriate user from the 'users' tab on the left.
        </Typography>
    </Box>}
  </Fragment>

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <GalvanalyserIcon className={classes.icon} />
        {createdUser !== null? createdUserContent : formContent}
      </div>
    </Container>
  )
}
