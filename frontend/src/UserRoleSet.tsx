// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import Connection, {User} from './APIConnection'
import React, {Component} from "react";
import IconButton from "@mui/material/IconButton";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";
import AddIcon from '@mui/icons-material/Add';
import Typography from "@mui/material/Typography";
import Tooltip from "@mui/material/Tooltip";
import Divider from "@mui/material/Divider";
import Avatar from "@mui/material/Avatar";
import Popover from "@mui/material/Popover";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import Box from "@mui/material/Box";

export type UserSet = {
  id: number;
  url: string;
  name: string;
  description?: string;
  is_admin?: boolean;
  users: User[];
}

export type UserSetProps = {
  user_sets: UserSet[];
  last_updated: Date;
  set_last_updated: (date: Date) => void;
  editable?: boolean;
}

type UserSetState = {
  all_users: User[]
}

type AddUserButtonProps = {
  user_set: UserSet;
  all_users: User[];
  set_last_updated: (date: Date) => void;
  [key: string]: any
}

export const user_in_sets = (sets: UserSet[]) => {
  if (Connection.user === null)
    return false
  for (const set of sets) {
    if (set.users.find(u => u.id === Connection.user?.id))
      return true
  }
  return false
}

function AddUserButton(props: AddUserButtonProps) {
  const [anchorEl, setAnchorEl] = React.useState<HTMLButtonElement | null>(null);

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleChange = (event: React.SyntheticEvent, value: any) => {
    handleClose()
    console.log(value)
    Connection.fetch(
      `${props.user_set.url}add/`,
      {method: 'POST', body: JSON.stringify({user: value.id})}
    )
      .then(() => props.set_last_updated(new Date()))
  }

  const open = Boolean(anchorEl);
  const id = open ? `add-user-button-${props.user_set.id}` : undefined;

  const exclude_user_ids = props.user_set.users.map(u => u.id)
  const users_to_include = props.all_users.filter(u => !exclude_user_ids.includes(u.id))

  return (
    <div key={`add-user-button-wrapper-${props.user_set.id}`}>
      <IconButton
        aria-describedby={id}
        onClick={handleClick}
        size={'small'}
      >
        <AddIcon/>
      </IconButton>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
      >
        <Box sx={{height: 200}}>
          <Autocomplete
            disablePortal
            id={`user-select-${props.user_set.id}`}
            options={users_to_include.map(u => ({label: u.username, id: u.id}))}
            sx={{ width: 300 }}
            onChange={handleChange}
            isOptionEqualToValue={((option, value) => option.id === value.id)}
            renderInput={(params) => <TextField {...params} label="Select user" />}
          />
        </Box>
      </Popover>
    </div>
  );
}

/**
 * Return lists of user roles that we can assign users to/delete users from.
 */
export default class UserRoleSet extends Component<UserSetProps, UserSetState> {

  constructor(props: UserSetProps) {
    super(props);
    this.state = {all_users: []}
  }

  async componentDidMount() {
    Connection.fetchMany<User>('users/')
      .then(results => results.map(r => r.content))
      .then(r => this.setState({all_users: r}))
  }

  handleDelete(user_id: number, group_url: string) {
    Connection.fetch(
      `${group_url}remove/`,
      {method: 'POST', body: JSON.stringify({user: user_id})}
    ).then(() => this.props.set_last_updated(new Date()))
  }

  editable: boolean = this.props.editable !== false
  _parent_group: UserSet|null = null
  _subsequent_editable: boolean = this.editable

  // Work out permissions for each group
  is_set_editable = this.props.user_sets.map(u => {
    const editable = this._subsequent_editable ||
      (this.editable && Connection.user && u.users.map(usr => usr.id).includes(Connection.user.id))
    if (editable && u.is_admin)
      this._subsequent_editable = true
    const out = {id: u.id, editable: this.editable && editable, parent: this._parent_group}
    this._parent_group = u
    return out
  })

  get user_sets() {
    return this.props.user_sets.map(u => <div key={`div-${u.id}`}>
      <Tooltip title={u.description || ""} key={`divider-${u.id}`} placement={'left'}>
        <Divider>
          {u.name}
        </Divider>
      </Tooltip>
      <Stack key={`stack-${u.id}`}  direction="row" spacing={1} justifyContent="flex-end" alignItems="center">
        {u.users.map(usr => {
          const editability = this.is_set_editable.find(s => s.id === u.id)
          const editable = editability?.editable
          const undeleteable = u.is_admin && u.users.length + (editability?.parent?.users.length || 0) <= 1
          if (editable && undeleteable)
            return <Tooltip
              title={"Cannot be deleted because at least one administrator must be present."}
              key={`user_set-${u.id}_${usr.id}`}
              placement="left"
            >
              <Chip
                avatar={<Avatar alt={usr.username}/>}
                label={<Typography noWrap>{usr.username}</Typography>}
                size={'small'}
              />
            </Tooltip>
          else if (editable)
            return <Chip
              key={`user_set-${u.id}_${usr.id}`}
              onDelete={() => this.handleDelete(usr.id, u.url)}
              avatar={<Avatar alt={usr.username}/>}
              label={<Typography noWrap>{usr.username}</Typography>}
              size={'small'}
            />
          else
            return <Chip
              key={`user_set-${u.id}_${usr.id}`}
              avatar={<Avatar alt={usr.username}/>}
              label={<Typography noWrap>{usr.username}</Typography>}
              size={'small'}
            />
        })}
        {
          this.is_set_editable.find(s => s.id === u.id)?.editable &&
            <AddUserButton
                key={`user_set-add-${u.id}`}
                user_set={u}
                all_users={this.state.all_users}
                set_last_updated={this.props.set_last_updated}
            />
        }
      </Stack>
    </div>)
  }

  render() {
    return this.user_sets;
  }
}