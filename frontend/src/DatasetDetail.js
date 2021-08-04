import React, { useEffect, useState } from "react";
import Typography from '@material-ui/core/Typography';
import { useForm } from "react-hook-form";
import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import { makeStyles } from '@material-ui/core/styles';
import SaveIcon from '@material-ui/icons/Save';
import IconButton from '@material-ui/core/IconButton';
import Container from '@material-ui/core/Container';
import { useParams } from "react-router-dom";
import {
  FormTextField, FormSelectField, 
  FormAutocompleteField, FormMultiSelectField,
} from './FormComponents'
import { 
  datasets, users, cells, update_dataset, equipment
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


export default function DatasetDetail() {
  const { id } = useParams();
  const classes = useStyles();

  const { control, handleSubmit } = useForm();

  const [cellData, setCellData] = useState([])
  const [equipmentData, setEquipmentData] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [userData, setUserData] = useState([])

  useEffect(() => {
    users().then((response) => {
      if (response.ok) {
        response.json().then(setUserData);
      }
    });
    cells().then((response) => {
      if (response.ok) {
        return response.json().then(setCellData);
      }
    });
    datasets(id).then((response) => {
      if (response.ok) {
        response.json().then((d) => {
          d['cell_id'] = d.cell ? d.cell.id : null
          d['owner_id'] = d.owner ? d.owner.id : null
          d['equipment'] = d.equipment.map(x => x.id)
          setDataset(d);
        });
      }
    });
    equipment().then((response) => {
      if (response.ok) {
        response.json().then((d) => {
          setEquipmentData(d);
        });
      }
    });
  }, [id]);

  const onSubmit = (values) => {
    update_dataset(dataset.id, values);
  };


  if (!equipmentData || !dataset || !cellData || !userData) {
    return (null);
  }


  let cellOptions = cellData.map(cell => (
    {key: cell.name, value: cell.id}
  ));
  cellOptions.push({key: "None", value: null})
  let userOptions = userData.map(user => (
    {key: user.username, value: user.id}
  ));
  userOptions.push({key: "None", value: null})
  const equipmentOptions = equipmentData.map(e => (
    {key: e.name, value: e.id}
  ))

  const purposeOptions = [
    'Ageing',
    'Real world/drive cycling',
    'Characterisation/check-up',
    'Thermal performance',
    'Pulse',
    'Charge',
    'Discharge',
    'EIS',
    'GITT',
    'Pseudo-OCV',
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
      <FormTextField 
        control={control}
        defaultValue={dataset.name}
        name="name"
        label="Dataset Name"
        style={{ width: 320 }}
      />

      <FormSelectField
        control={control}
        defaultValue={dataset.cell_id || ''}
        name="cell_id"
        label="Cell"
        style={{ width: 380 }}
        options={cellOptions}
      />
      <FormSelectField
        control={control}
        name="owner_id"
        label="Owner"
        defaultValue={dataset.owner_id || ''}
        options={userOptions}
        style={{ width: 250 }}
      />
      <FormAutocompleteField
        control={control}
        name="purpose"
        defaultValue={dataset.purpose}
        label="Purpose of the experiment"
        options={purposeOptions}
        style={{ width: 500 }}
      />
      <FormMultiSelectField
        control={control}
        name="equipment"
        label="Test Equipment Used"
        defaultValue={dataset.equipment}
        options={equipmentOptions}
        style={{ width: 500 }}
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
