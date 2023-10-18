import React, {useEffect, useState} from "react";
import {useDebouncedCallback} from "use-debounce";
import TextField, {TextFieldProps} from "@mui/material/TextField";
import Typography, {TypographyProps} from "@mui/material/Typography";
import {SvgIconProps} from "@mui/material/SvgIcon"
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import PrettyObject from "./PrettyObject";
import Checkbox, {CheckboxProps} from "@mui/material/Checkbox";
import PrettyArray from "./PrettyArray";

type PrettifyProps = {
    target: any
    nest_level: number
    edit_mode: boolean
    onEdit?: (value: any) => void
    clearParentFocus?: () => void
}

type PrettyComponentProps = {
    value: any
    onChange: (value: any) => void
    edit_mode: boolean
}

export const PrettyString = (
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps & (TextFieldProps | TypographyProps)
) => edit_mode?
    <TextField
        label="Value"
        variant="filled"
        size="small"
        multiline={true}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...childProps as TextFieldProps}
    /> :
    <Typography component="span" variant="body1" {...childProps as TypographyProps}>{value}</Typography>

const PrettyNumber = (
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps & (TextFieldProps | TypographyProps)
) => {
    const [error, setError] = useState<boolean>(false)
    return edit_mode ?
        <TextField
            type="number"
            label="Value"
            variant="filled"
            size="small"
            inputProps={{inputMode: 'numeric', pattern: '-?[0-9]*[.,]?[0-9]*'}}
            error={error}
            value={value}
            onChange={(e) => {
                let v: number
                try {v = parseFloat(e.target.value)} catch (e) {
                    setError(true)
                    return
                }
                setError(false)
                onChange(v)
            }}
            {...childProps as TextFieldProps}
        /> :
        <Typography component="span" variant="overline" sx={{fontSize: "1.1em"}} {...childProps as TypographyProps}>
            {value}
        </Typography>
}

const PrettyBoolean = (
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps & (CheckboxProps | SvgIconProps)
) => edit_mode?
    <Checkbox
        sx={{fontSize: "1.1em"}}
        value={value}
        onChange={(e) => onChange(!!e.target.value)}
        {...childProps as CheckboxProps}
    /> :
    value? <CheckIcon {...childProps as SvgIconProps} /> : <ClearIcon {...childProps as SvgIconProps} />

export default function Prettify(props: PrettifyProps) {
    const [value, setValue] = useState<any>(props.target)
    useEffect(() => {
        setValue(props.target)
    }, [props.target])
    const debounced = useDebouncedCallback(
        props.onEdit? (value: any) => props.onEdit!(value) : () => {},
        500
    )
    const on_change = (v: any) => {
        setValue(v)
        debounced(v)
    }
    const child_props = {value, onChange: on_change, edit_mode: props.edit_mode}

    if (props.edit_mode && typeof props.onEdit !== 'function')
        throw new Error(`onEdit must be a function if edit_mode=true`)

    if (value === null || value === undefined) return <></>
    if (typeof value === 'string')
        return <PrettyString {...child_props} />
    if (typeof value === 'number')
        return <PrettyNumber {...child_props} />
    if (typeof value === 'boolean')
        return <PrettyBoolean {...child_props} />
    if (value instanceof Array) {
        return <PrettyArray
            nest_level={props.nest_level + 1}
            edit_mode={props.edit_mode}
            target={value}
            onEdit={props.onEdit}
            clearParentFocus={props.clearParentFocus}
        />
    }
    if (typeof value === 'object') {
        return <PrettyObject
            nest_level={props.nest_level + 1}
            edit_mode={props.edit_mode}
            onEdit={props.onEdit}
            target={value}
            clearParentFocus={props.clearParentFocus}
        />
    }

    console.error("Prettify failure", props)
    throw new Error(`Could not prettify value: ${value}`)
}