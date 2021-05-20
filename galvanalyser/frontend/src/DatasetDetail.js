import React, { useEffect, useState } from "react";
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography';
import { useForm, Controller  } from "react-hook-form";
import Card from "@material-ui/core/Card";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import MenuItem from '@material-ui/core/MenuItem';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper';
import SaveIcon from '@material-ui/icons/Save';
import IconButton from '@material-ui/core/IconButton';
import FormControl from '@material-ui/core/FormControl';
import InputLabel from '@material-ui/core/InputLabel';
import Select from '@material-ui/core/Select';
import Container from '@material-ui/core/Container';
import { useParams } from "react-router-dom";
import { 
  datasets, users, cells, update_dataset
} from './Api'
import DatasetChart from './DatasetChart'

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    height: '100%',
  },
  formInput: {
    margin: theme.spacing(1),
  },
}));


const renderTextField = (
  { input, label, meta: { touched, error }, ...custom },
) => (
  <TextField
    hintText={label}
    floatingLabelText={label}
    errorText={touched && error}
    {...input}
    {...custom}
  />
);

export default function DatasetDetail() {
  const { id } = useParams();
  const classes = useStyles();

  const { control, handleSubmit, reset } = useForm({
    name: 'name', cell_id: 'cell_id', owner: 'owner',
    test_equipment: 'test_equipment', purpose: 'purpose'
  });

  const [cellData, setCellData] = useState([])
  const [dataset, setDataset] = useState(null)
  const [userData, setUserData] = useState([])

  useEffect(() => {
    users().then((response) => {
      if (response.ok) {
        response.json().then(setUserData);
      }
    });
  }, []);

  useEffect(() => {
    cells().then((response) => {
      if (response.ok) {
        return response.json().then(setCellData);
      }
    });
  }, []);

  const onSubmit = (values) => {
    console.log(JSON.stringify(values));
    update_dataset(dataset.id, values)
  };

  console.log('rendering with id', id);
  console.log('rendering with dataset', dataset);

  useEffect(() => {
    datasets(id).then((response) => {
      if (response.ok) {
        response.json().then((d) => {
          setDataset(d);
          reset(d);
        });
      }
    });
  }, []);


  if (dataset === null) {
    return (null);
  }

  const purposeOptions = [
      'purpose1',
      'purpose2',
      'purpose3',
  ]

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Typography variant="h5">
          {dataset.name} - {dataset.date} - {dataset.dataset_type}
      </Typography>
      <DatasetChart dataset={dataset} />
      <form onSubmit={handleSubmit(onSubmit)} autoComplete="off">
      <Card style={{display: 'inline-block'}}>
      <CardContent>
      <Controller
        control={control}
        defaultValue=""
        name="name"
        render={({ field }) => (
          <TextField className={classes.formInput} 
            style={{ width: 320 }}
            {...field} 
            label="Dataset Name" 
          />
        )}
      />
      <Controller
        control={control}
        defaultValue=""
        name="cell_id"
        render={({ field }) => (
          <Autocomplete
            {...field}
            className={classes.formInput}
            options={cellData}
            renderInput={(params) => 
              <TextField  {...params} style={{ width: 360}} label="Cell Used"/>
            }
            getOptionLabel={(option) => typeof option === "object" ? option.uid : option.toString()}
            getOptionSelected={option => option.id}
            onChange={(_, data) => field.onChange(data.id)}
          />
        )}
      />
      <Controller
        control={control}
        name="owner"
        defaultValue=""
        render={({ field }) => (
          <Autocomplete
            {...field}
            className={classes.formInput}
            options={userData}
            renderInput={(params) => 
              <TextField  {...params} style={{ width: 250}} label="Owner"/>
            }
            getOptionLabel={(option) => typeof option === "string" ? option: option.username}
            getOptionSelected={option => option.username}
            onChange={(_, data) => field.onChange(data.username)}
          />
        )}
      />
      <Controller
        control={control}
        name="purpose"
        defaultValue=""
        render={({ field }) => (
          <Autocomplete
            {...field}
            freeSolo
            className={classes.formInput}
            options={purposeOptions}
            
            renderInput={(params) => 
              <TextField  {...params} style={{ width: 500 }} label="Purpose of experiment"/>
            }
            onChange={(_, data) => field.onChange(data)}
          />
        )}
      />
      <Controller
        control={control}
        name="test_equipment"
        defaultValue=""
        render={({ field }) => (
          <TextField  
            style={{ width: 500 }}
            {...field} label="Test Equipment Used" 
            className={classes.formInput}
          />
        )}
      />

      </CardContent>
      <CardActions disableSpacing>
        <IconButton type="submit">
          <SaveIcon/>
        </IconButton>
      </CardActions>
    </Card>
    </form>
    </Container>
  );
}
