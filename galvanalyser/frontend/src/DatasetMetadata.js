import React, { useEffect, useState } from "react";
import { metadata, update_metadata, add_metadata} from './Api'
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';

const useStyles = makeStyles((theme) => ({
  root: {
    '& .MuiTextField-root': {
      margin: theme.spacing(1),
      width: '25ch',
    },
  },
}));

export default function DatasetMetadata(props) {
  const { dataset } = props;
  const classes = useStyles();

  const [dsMetadata, setDsMetadata] = useState({})

  useEffect(() => {
    metadata(dataset.id).then((response) => {
      if (response.ok) {
        return response.json().then(setDsMetadata);
      }
    });
  }, [dataset])

  const handleAddMetadata = () => {
    add_metadata(dataset.id, dsMetadata).then((response) => {
      if (response.ok) {
        return response.json().then(setDsMetadata);
      }
    });
  };

  const handleChange = () => {
    console.log('change!');
  };

  console.log('metadata', dsMetadata)
  if (Object.keys(dsMetadata).length === 0)
    return (
      <Button variant="contained" onClick={handleAddMetadata}>
        Add Metadata
      </Button>
    )
  else {
    return (
      <form className={classes.root} noValidate autoComplete="off">
      <TextField id="cell_uid" label="Cell" value={dsMetadata.cell_uid} onChange={handleChange} />
      <TextField id="json_data" label="Other" value={dsMetadata.json_data} onChange={handleChange} />
      <TextField id="owner" label="Owner" value={dsMetadata.owner} onChange={handleChange} />
      <TextField id="purpose" label="Purpose" value={dsMetadata.purpose} onChange={handleChange} />
      <TextField id="test_equipment" label="Test Equipment" value={dsMetadata.test_equipment} onChange={handleChange} />
      </form>
    )
  }
 
}
