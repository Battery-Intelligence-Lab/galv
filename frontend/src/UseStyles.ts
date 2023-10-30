// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import { makeStyles } from 'tss-react/mui';
import {Theme} from "@mui/material/styles";

const item = (theme: Theme) => ({
  " .MuiCardHeader-root": {
    paddingBottom: 0,
    " .MuiAvatar-root": {
      borderRadius: theme.spacing(0.5)
    },
    " .MuiLink-root": {
      color: "inherit",
      textDecoration: "none",
      "&:hover": {
        textDecoration: "underline"
      }
    },
    " .MuiCardHeader-title": {
      fontSize: "large",
    }
  },
  " .MuiCardContent-root": {
    paddingTop: theme.spacing(0.5)
  }
})
export default makeStyles()((theme) => {
  return {
    button: {
      margin: theme.spacing(1),
    },
    chips: {
      display: 'flex',
      flexWrap: 'wrap',
    },
    chip: {
      margin: 2,
    },
    container: {
      paddingTop: theme.spacing(4),
      paddingBottom: theme.spacing(4),
      fontFamily: 'Helvetica Neue,Helvetica,Arial,sans-serif',
    },
    deleteIcon: {
      "&:hover": {color: theme.palette.error.light},
      "&:focus": {color: theme.palette.error.light}
    },
    head: {
      backgroundColor: theme.palette.primary.light,
    },
    headCell: {
      color: theme.palette.common.black,
    },
    iconButton: {
      padding: 10,
    },
    infoIcon: {
      "&:hover": {color: theme.palette.info.light},
      "&:focus": {color: theme.palette.info.light}
    },
    input: {
      marginLeft: theme.spacing(0),
      flex: 1,
    },
    inputAdornment: {
      color: theme.palette.text.disabled,
    },
    newTableCell: {paddingTop: theme.spacing(4)},
    newTableRow: {},
    paper: {marginBottom: theme.spacing(2)},
    refreshIcon: {
      "&:hover": {color: theme.palette.warning.light},
      "&:focus": {color: theme.palette.warning.light}
    },
    resize: {
      fontSize: '10pt',
    },
    saveIcon: {
      "&:hover": {color: theme.palette.success.light},
      "&:focus": {color: theme.palette.success.light}
    },
    table: {
      minWidth: 650,
    },

    text: {},
    page_title: {
      marginBottom: theme.spacing(2),
      color: theme.palette.text.secondary,
    },
    item_chip: {
      margin: theme.spacing(0.5),
      borderRadius: theme.spacing(0.5),
      borderColor: "transparent",
      "&:hover": {
        borderColor: theme.palette.primary.light,
        " .MuiSvgIcon-root": {
          color: theme.palette.primary.light
        }
      },
      " .MuiSvgIcon-root": {
        width: "1em",
        height: "1em",
      }
    },
    item_card: {
      ...item(theme)
    },
    item_page: {
      ...item(theme),
      marginTop: theme.spacing(2)
    },
    team_chip: {},
    error: {color: theme.palette.error.main},
    count_badge: {
      " .MuiBadge-badge": {
        backgroundColor: theme.palette.grey.A100,
        color: theme.palette.grey.A700,
      },
    },
    pretty_table: {
      backgroundColor: theme.palette.background.paper,
      "& td, & th": {
        border: "none",
        verticalAlign: "top",
      },
      "& tr:not(:first-of-type)": {
        "& > td, & > th": {
          paddingTop: 0,
        }
      },
      "& th": {
        textAlign: "right",
        paddingRight: 0,
        paddingLeft: theme.spacing(1),
        color: theme.palette.text.disabled,
        "& .MuiTypography-root": {
          fontWeight: "bold"
        },
        "& *": {
          textAlign: "right",
        }
      }
    },
    pretty_array: {
      backgroundColor: theme.palette.background.paper,
      "& .MuiListItem-root": {
        paddingLeft: theme.spacing(0.5),
        "& .MuiListItemIcon-root": {
          minWidth: theme.spacing(1),
          marginRight: theme.spacing(0.5),
          marginTop: 0,
        }
      }
    },
    pretty_nested: {
      backgroundColor: theme.palette.grey.A100,
    },
    pretty_select: {
        width: 300,
    },
    type_changer_button: {},
    type_changer_popover: {
      zIndex: 5,
    },
    type_changer_resource_popover: {}
  }
});
