// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {Fragment, useState} from 'react';
import TextField from '@mui/material/TextField';
import Paper from '@mui/material/Paper';
import AddIcon from '@mui/icons-material/Add';
import Container from '@mui/material/Container';
import SaveIcon from '@mui/icons-material/Save';
import AsyncTable from './AsyncTable';
import Connection from "./APIConnection";
import ActionButtons from "./ActionButtons";
import useStyles from "./UseStyles";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";
import CardContent from "@mui/material/CardContent";
import Card from "@mui/material/Card";
import Stack from "@mui/material/Stack";

export type TokenFields = {
  url: string;
  id: number;
  name: string;
  created: string;
  expiry: string|null;
}

export type CreateTokenFields = TokenFields & {token: string}

const columns = [
  {label: 'Name', help: 'Token Name'},
  {label: 'Created', help: 'Creation time'},
  {label: 'Expires', help: 'Expiry time'},
  {label: 'Actions', help: 'Tokens can be renamed or revoked. Revoked tokens can no longer be used.'},
]

const datetimeOptions: Intl.DateTimeFormatOptions = {
  year: 'numeric', month: 'numeric', day: 'numeric',
  hour: 'numeric', minute: 'numeric', second: 'numeric',
};

const expiryOptions: {name: string, value: string}[] = [
  {name: '1 hour', value: (60 * 60).toString()},
  {name: '1 day', value: (60 * 60 * 24).toString()},
  {name: '1 week', value: (60 * 60 * 24 * 7).toString()},
  {name: '4 weeks', value: (60 * 60 * 24 * 7 * 4).toString()},
  {name: '6 months', value: (60 * 60 * 24 * 7 * 4 * 6).toString()},
  {name: '1 year', value: (60 * 60 * 24 * 365).toString()}
]

export default function Tokens() {
  const { classes } = useStyles();

  const [newToken, setNewToken] = useState<string>('')

  const createToken = (name: string, expires_after_s: number|null) => {
    const insert_data = {name, ttl: expires_after_s}
    return Connection.fetch<CreateTokenFields>('create_token/', {body: JSON.stringify(insert_data), method: 'POST'})
      .then(r => setNewToken(r.content.token))
  };

  const updateToken = (data: TokenFields) => {
    const insert_data = {name: data.name}
    return Connection.fetch(data.url, {body: JSON.stringify(insert_data), method: 'PATCH'})
      .then(r => r.content)
      .then(c => {
        setNewToken('')
        return c
      })
  };

  const deleteToken = (data: TokenFields) => Connection.fetch(data.url, {method: 'DELETE'})
    .then(() => setNewToken(''))

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Stack spacing={2}>
        {
          newToken !== '' && <Card>
                <CardContent>
                    <Typography gutterBottom variant="h5" component="div">
                        New token created.
                    </Typography>
                    <Typography gutterBottom color="text.secondary">
                        Please copy the token below for use in your application.
                        You will not be able to see or change this token later.
                        If you need to alter this token later, you must destroy
                        and replace it.
                    </Typography>
                    <Typography textAlign="center">
                      {newToken}
                    </Typography>
                </CardContent>
            </Card>
        }
        <Paper className={classes.paper}>
          <AsyncTable<TokenFields>
            classes={classes}
            columns={columns}
            row_generator={(token, context) => [
              <Fragment key="Name">
                <TextField
                  name="name"
                  value={token.name}
                  InputProps={{
                    classes: {
                      input: classes.resize,
                    },
                  }}
                  placeholder="New token name"
                  onChange={context.update}
                />
              </Fragment>,
              context.is_new_row? <Fragment key="Created"/> : <Fragment key="Created">{
                Intl.DateTimeFormat('en-GB', datetimeOptions).format(
                  Date.parse(token.created)
                )}
              </Fragment>,
              context.is_new_row? <Fragment key="Expires">
                <Select
                  key='select'
                  id={`expiry-select`}
                  name="expiry"
                  value={token.expiry || ''}
                  sx={{minWidth: 100}}
                  onChange={(e) => context.update_direct('expiry', e.target.value)}
                >
                  <MenuItem key="none" value=""><em>Never</em></MenuItem>
                  {expiryOptions.map(o => <MenuItem key={o.value} value={o.value}>{o.name}</MenuItem>)}
                </Select>
              </Fragment> : <Fragment key="Expires">
                {
                  token.expiry? Intl.DateTimeFormat('en-GB', datetimeOptions).format(
                    Date.parse(token.expiry)
                  ) : <em>Never</em>
                }
              </Fragment>,
              <Fragment key="actions">
                <ActionButtons
                  classes={classes}
                  onSave={
                    context.is_new_row?
                      () => createToken(token.name, token.expiry? parseInt(token.expiry) : null)
                        .then(() => context.refresh_all_rows(false)) :
                      () => updateToken(token).then(context.refresh)
                  }
                  saveButtonProps={{disabled: !context.value_changed}}
                  saveIconProps={{component: context.is_new_row? AddIcon : SaveIcon}}
                  onDelete={
                    () =>
                      window.confirm(`Delete token ${token.name}?`) &&
                      deleteToken(token).then(() => context.refresh_all_rows())
                  }
                  deleteButtonProps={{disabled: context.is_new_row}}
                />
              </Fragment>
            ]}
            new_row_values={{name: '', created: '', expiry: ''}}
            url={`tokens/`}
            styles={classes}
          />
        </Paper>
      </Stack>
    </Container>
  );
}
