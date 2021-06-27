import React from "react";
import TextField from '@material-ui/core/TextField';
import { makeStyles } from '@material-ui/core/styles';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import Autocomplete from '@material-ui/lab/Autocomplete';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import { Controller  } from "react-hook-form";
//import DateFnsUtils from '@date-io/date-fns'; // choose your lib
//import { DateTimePicker } from '@material-ui/pickers';
import Chip from '@material-ui/core/Chip';

const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    height: '100%',
  },
  formInput: {
    margin: theme.spacing(1),
    width: '100%',
  },
  chips: {
    display: 'flex',
    flexWrap: 'wrap',
  },
  chip: {
    margin: 2,
  },
}));

//export function FormDateTimeField({control, name, defaultValue, label, ...rest}) {
//  const classes = useStyles();
//  return (
//    <Controller
//        control={control}
//        defaultValue={defaultValue}
//        name={name}
//        render={({ field }) => (
//          <DateTimePicker
//            className={classes.formInput} 
//            format="dd/MM/yyyy HH:mm"
//            {...rest} 
//            {...field} 
//            label={label}
//          />
//        )}
//      />
//  )
//}

export function FormTextField({control, name, defaultValue, label, ...rest}) {
  const classes = useStyles();
  return (
    <Controller
        control={control}
        defaultValue={defaultValue}
        name={name}
        render={({ field }) => (
          <TextField 
            className={classes.formInput} 
            {...rest} 
            {...field} 
            label={label}
          />
        )}
      />
  )
}

export function FormMultiSelectField({control, name, defaultValue, label, options, ...rest}) {
  const classes = useStyles();
  return (
    <FormControl className={classes.formInput}>
    <InputLabel id={name.concat('-select-label')}>
      {label}
    </InputLabel>
    <Controller
        control={control}
        defaultValue={defaultValue}
        name={name}
        render={({ field }) => (
        <Select
          labelId={name.concat('-select-label')}
          multiple
          renderValue={(selected) => (
            <div className={classes.chips}>
              {selected.map(value => (
                <Chip 
                  key={value} 
                  label={options.find(x => x.value === value).key} 
                  className={classes.chip} 
                />
              ))}
            </div>
          )}
          {...rest}
          {...field}
        >
          {options.map(option => {
            return (
              <MenuItem key={option.value} value={option.value}>{option.key}</MenuItem>
            )
          })}
        </Select>
        )}
      />
      </FormControl>
  )
}

export function FormAutocompleteField({control, name, defaultValue, label, options, ...rest}) {
  const classes = useStyles();

  return (
    <Controller
        control={control}
        defaultValue={defaultValue}
        name={name}
        render={({ field }) => (
          <Autocomplete
            {...field}
            {...rest}
            className={classes.formInput}
            options={options}
            renderInput={(params) => 
              <TextField  {...params} label={label}/>
            }
            onChange={(_, data) => field.onChange(data)}
          />
        )}
      />
  )
}

export function FormSelectField({control, name, defaultValue, label, options, ...rest}) {
  const classes = useStyles();
  return (
    <FormControl className={classes.formInput}>
    <InputLabel id={name.concat('-select-label')}>
      {label}
    </InputLabel>
    <Controller
        control={control}
        defaultValue={defaultValue}
        name={name}
        render={({ field }) => (
        <Select
          labelId={name.concat('-select-label')}
          {...rest}
          {...field}
        >
          {options.map(option => {
            return (
              <MenuItem key={option.value} value={option.value}>{option.key}</MenuItem>
            )
          })}
        </Select>
        )}
      />
      </FormControl>
  )
}
