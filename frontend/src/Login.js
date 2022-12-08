import {login} from "./Api"
import { makeStyles } from '@mui/styles'
import React, { useState, useRef } from "react";
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import Alert from '@mui/lab/Alert';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { useNavigate } from "react-router-dom";
import { ReactComponent as GalvanalyserIcon} from './Galvanalyser-icon.svg';

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
}));


export default function Login({ onLogin }) {
  const classes = useStyles();
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  const navigate = useNavigate();

  const submit = useRef(null);
  const username_input = useRef(null);
  const password_input = useRef(null);

  const handleEnterKey = (e) => {
    if(e.key === "Enter") {
      if (username === "") username_input.current.focus();
      else if (password === "") password_input.current.focus();
      else submit.current.click();
    }
  }

  const onSubmitClick = (e)=>{
    e.preventDefault()
    console.log("You pressed login")
    if (username === "") username_input.current.focus();
    else if (password === "") password_input.current.focus();
    else {
      login(username, password).then(r => {
        if (!r.ok) {
          console.log(r, r.data)
          return r.json().then(data=>setError(data.message));
        }
        return r.json().then(data => {
          setError('')
          onLogin(data)
          navigate('/');
        })
      });
    }
  }

  const handleUsernameChange = (e) => {
    setUsername(e.target.value)
  }

  const handlePasswordChange = (e) => {
    setPassword(e.target.value)
  }

  return (
    <Container component="main" maxWidth="xs">
      <CssBaseline />
      <div className={classes.paper}>
        <GalvanalyserIcon className={classes.icon}/>
        <Typography component="h1" variant="h5">
          Sign in
        </Typography>
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
          Sign In
        </Button>
        </form>
      </div>
    </Container>
  )
}
