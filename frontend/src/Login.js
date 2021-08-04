import {login} from "./Api"
import { makeStyles } from '@material-ui/core/styles';
import React, { useState } from "react";
import Button from '@material-ui/core/Button';
import CssBaseline from '@material-ui/core/CssBaseline';
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import Container from '@material-ui/core/Container';
import { useHistory } from "react-router-dom";
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


export default function Login() {
  const classes = useStyles();
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const history = useHistory();

  const onSubmitClick = (e)=>{
    e.preventDefault()
    console.log("You pressed login")
    login(username, password).then(r => {
      if (r.ok) {
        return r.json();
      }
      console.log('login failed');
      console.log("Please type in correct username/password")
    }).then(response => {
        console.log('login success', response);          
        history.push('/');
    });
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
          id="password"
          autoComplete="current-password"
        />
        <Button
          type="submit"
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
