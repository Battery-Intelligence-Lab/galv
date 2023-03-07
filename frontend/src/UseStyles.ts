import {makeStyles} from "@mui/styles";

export default makeStyles((theme) => ({
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
}));
