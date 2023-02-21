import React, { Fragment } from 'react';
import Paper from '@mui/material/Paper';
import Container from '@mui/material/Container';
import HowToRegIcon from '@mui/icons-material/HowToReg';
import AsyncTable from './AsyncTable';
import Connection, {User} from "./APIConnection";
import useStyles from "./UseStyles";
import Typography from '@mui/material/Typography';
import IconButton from "@mui/material/IconButton";

const columns = [
  {label: 'Username'},
  {label: 'Activate', help: 'Authorize a user to access Galvanalyser'}
]

export default function ActivateUsers() {
  const classes = useStyles();

  const activateUser = (user: User) => Connection.fetch(`${user.url}vouch_for/`);

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <AsyncTable<User>
          classes={classes}
          columns={columns}
          row_generator={(user, context) => [
            <Fragment>
                <Typography>{user.username}</Typography>
            </Fragment>,
            <Fragment key="actions">
              <IconButton
                color="primary"
                onClick={() => activateUser(user).then(() => context.refresh_all_rows(false))}
              >
                <HowToRegIcon />
              </IconButton>
            </Fragment>
          ]}
          url={`inactive_users/`}
          styles={classes}
        />
      </Paper>
    </Container>
  );
}