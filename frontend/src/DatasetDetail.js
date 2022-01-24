import React, { useEffect, useState } from "react";
import Typography from '@material-ui/core/Typography';
import { useForm } from "react-hook-form";
import Card from "@material-ui/core/Card";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import { makeStyles } from '@material-ui/core/styles';
import SaveIcon from '@material-ui/icons/Save';
import IconButton from '@material-ui/core/IconButton';
import DoneIcon from '@material-ui/icons/Done';
import Button from '@material-ui/core/Button';
import {getToken} from "./Api"
import Alert from '@material-ui/lab/Alert';
import Container from '@material-ui/core/Container';
import CircularProgress from '@material-ui/core/CircularProgress';
import Box from '@material-ui/core/Box';
import { green } from '@material-ui/core/colors';
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
  circularProgressWrapper: {
    m: 1, 
    position: 'relative' 
  },
  uploadButton: {
  },
  uploadButtonSuccess: {
    "&:disabled":{
        backgroundColor: green[500],
    }
  },
  circularProgress: {
    color: green[500],
    position: 'absolute',
    top: '50%',
    left: '50%',
    marginTop: '-12px',
    marginLeft: '-12px',
  },
  formInput: {
    margin: theme.spacing(1),
  },
}));

function DatasetForm({ dataset, setDataset, cellData, userData, equipmentData }) {
  const classes = useStyles();
  const [datasetError, setDatasetError] = useState(null)
  const [uploadTrackerId, setUploadTrackerId] = React.useState(null);
  const [uploadSuccess, setUploadSuccess] = React.useState(false);
  const { reset, control, handleSubmit, formState: {isDirty} } = useForm({
    defaultValues: dataset
  });
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
  const timer = React.useRef();
  const baseUrl = 'http://143.198.98.214:4000/ga/publish/'

  useEffect(() => {
    const pollUpload = () => {
      fetch(baseUrl + `status/${uploadTrackerId}`).then((response) => {
        return response.json()
      }).then(data => {
        console.log('upload status is:', data)
        if (data.status === 'FINISHED') {
          setUploadTrackerId(null)
          setUploadSuccess(true)
          clearInterval(timer.current)
        }
      }).catch(error => {
        console.log('error in battery archive upload status:', error)
      })
    }
    if (uploadTrackerId) {
      timer.current = setInterval(() => {
        pollUpload(uploadTrackerId);
      }, 1000);
      return () => clearInterval(timer.current);
    } else {
      clearInterval(timer.current)
    }
  }, [uploadTrackerId]);

  const handleBatteryArchiveUpload = () => {
    if (!uploadTrackerId) {
      setUploadSuccess(false);
      getToken().then(response => response.json()).then(data => {
        const options = {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token: data.access_token }),
        }
        fetch(baseUrl + `${dataset.id}`, options).then((response) => {
          return response.json()
        }).then(data => {
          setUploadTrackerId(data.tracker);
        }).catch(error => {
          console.log('error in battery archive upload:', error)
        })
      }).catch(error => {
        console.log('error in getting token for battery archive upload', error)
      })
    }
  };

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

  const onSubmit = (values) => {
    update_dataset(dataset.id, values).then(response => {
      if (response.ok) {
        const newDataset = {...dataset, ...values}
        setDataset(newDataset)
        setDatasetError(null)
        reset(newDataset)
      } else {
        response.json().then(data => setDatasetError(data.message))
      }
    });
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} autoComplete="off">
      <Card style={{display: 'inline-block'}}>
      <CardContent>
      <FormTextField 
        control={control}
        name="name"
        label="Dataset Name"
        style={{ width: 320 }}
      />

      <FormSelectField
        control={control}
        name="cell_id"
        label="Cell"
        style={{ width: 380 }}
        options={cellOptions}
      />
      <FormSelectField
        control={control}
        name="owner_id"
        label="Owner"
        options={userOptions}
        style={{ width: 250 }}
      />
      <FormAutocompleteField
        control={control}
        name="purpose"
        label="Purpose of the experiment"
        options={purposeOptions}
        style={{ width: 500 }}
      />
      <FormMultiSelectField
        control={control}
        name="equipment"
        label="Test Equipment Used"
        options={equipmentOptions}
        style={{ width: 500 }}
      />
      {datasetError &&
        <Alert severity="error">
          {datasetError}
        </Alert>
      }
      </CardContent>
      <CardActions disableSpacing>
        <IconButton type="submit" disabled={!isDirty}>
          <SaveIcon/>
        </IconButton>
        <Box className={classes.circularProgressWrapper}>
        { uploadSuccess &&
        <Button
          variant="contained" 
          onClick={handleBatteryArchiveUpload}
          className={classes.uploadButtonSuccess}
          disabled={true}
          endIcon={<DoneIcon />}
        >
          Upload to Battery Archive
        </Button>
        }
        { !uploadSuccess &&
        <Button
          variant="contained" 
          onClick={handleBatteryArchiveUpload}
          className={classes.uploadButton}
          disabled={uploadTrackerId}
        >
          Upload to Battery Archive
        </Button>
        }
        {uploadTrackerId && (
          <CircularProgress
            size={24}
            className={classes.circularProgress}
          />
        )}
      </Box>
      </CardActions>
    </Card>
    </form>
  )
}

export default function DatasetDetail() {
  const { id } = useParams();
  const classes = useStyles();

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

  if (!equipmentData || !dataset || !cellData || !userData) {
    return (null);
  }

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Typography variant="h5">
          {dataset.name} - {dataset.date} - {dataset.dataset_type}
      </Typography>
      {dataset &&
      <DatasetChart dataset={dataset} />
      }
      {dataset &&
      <DatasetForm 
        dataset={dataset} cellData={cellData} 
        userData={userData} equipmentData={equipmentData} 
        setDataset={setDataset}
      />
      }
    </Container>
  );
}
