import React, {PropsWithChildren, SyntheticEvent, useEffect, useState} from "react";
import TextField, {TextFieldProps} from "@mui/material/TextField";
import Typography, {TypographyProps} from "@mui/material/Typography";
import {SvgIconProps} from "@mui/material/SvgIcon"
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import PrettyObject from "./PrettyObject";
import Checkbox, {CheckboxProps} from "@mui/material/Checkbox";
import PrettyArray from "./PrettyArray";
import TypeChanger, {detect_type, Serializable, TypeChangerProps, TypeChangerSupportedTypeName} from "../utils/TypeChanger";
import Stack from "@mui/material/Stack";
import {ChipProps} from "@mui/material/Chip";
import {is_lookup_key} from "../../constants";
import PrettyResource from "./PrettyResource";

type PrettifyProps = {
    target: any
    nest_level?: number
    edit_mode?: boolean
    // onEdit is called when the user leaves the field
    // If it returns a value, the value is set as the new value for the field
    onEdit?: (value: Serializable) => Serializable|void
    lock_type_to?: TypeChangerSupportedTypeName
    // When type is an array, we can lock the type of the array's children.
    // This only works for one level of nesting, but that's all we need for official fields
    // which are the only fields where types are locked.
    lock_child_type_to?: TypeChangerSupportedTypeName
    hide_type_changer?: boolean
}

export type PrettyComponentProps = {
    value: any
    onChange: (value: any) => void
    edit_mode: boolean
}

export const PrettyString = (
    {value, onChange, edit_mode, ...childProps}:
        PrettyComponentProps & Partial<ChipProps | TextFieldProps | TypographyProps>
) => edit_mode ?
    <TextField
        label="value"
        variant="filled"
        size="small"
        multiline={false} // TODO fix error spam
        value={value}
        onChange={(e) => onChange(e.target.value)}
        {...childProps as TextFieldProps}
    /> :
    <Typography component="span" variant="body1" {...childProps as TypographyProps}>{value}</Typography>

const PrettyNumber = (
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps & Partial<TextFieldProps | TypographyProps>
) => {
    const [error, setError] = useState<boolean>(false)
    return edit_mode ?
        <TextField
            type="number"
            label="value"
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
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps &
        Partial<Omit<CheckboxProps, "onChange"> | SvgIconProps>
) => edit_mode?
    <Checkbox
        sx={{fontSize: "1.1em"}}
        checked={value}
        onChange={(e) => onChange(e.currentTarget.checked)}
        {...childProps as CheckboxProps}
    /> :
    value? <CheckIcon {...childProps as SvgIconProps} /> : <ClearIcon {...childProps as SvgIconProps} />

const TypeChangeWrapper = ({children, ...props}: PropsWithChildren<TypeChangerProps>) =>
    <Stack direction="row" spacing={0.5}>
        <TypeChanger {...props} />
        {children}
    </Stack>

export function Pretty(
    {target, nest_level, edit_mode, onEdit, lock_type_to, lock_child_type_to, ...childProps}: PrettifyProps &
        Partial<TextFieldProps | TypographyProps | Omit<CheckboxProps, "onChange"> | SvgIconProps | ChipProps>
) {
    const denull = (t: any) => t ?? ''
    const [value, setValue] = useState<any>(denull(target))
    useEffect(() => setValue(denull(target)), [target])
    const triggerEdit = () => {
        if (edit_mode && onEdit && value !== denull(target)) {
            const v = onEdit(value)
            console.log("triggerEdit", {value, v, target})
            if (v !== undefined) setValue(v)
        }
    }
    const props = {
        value,
        onChange: setValue,
        edit_mode: edit_mode,
        onBlur: triggerEdit,
        onKeyDown: (e: SyntheticEvent<any, KeyboardEvent>) => {
            if (e.nativeEvent.code === 'Enter') triggerEdit()
        }
    }

    if (edit_mode && typeof onEdit !== 'function')
        throw new Error(`onEdit must be a function if edit_mode=true`)

    const type = lock_type_to ?? detect_type(value)

    if (type === 'string')
        return <PrettyString {...props} {...childProps as Partial<TextFieldProps | TypographyProps>} />
    if (type === 'number')
        return <PrettyNumber {...props} {...childProps as Partial<TextFieldProps | TypographyProps>} />
    if (type === 'boolean')
        return <PrettyBoolean
            {...props}
            onChange={(v) => onEdit && onEdit(v)}
            {...childProps as Partial<Omit<CheckboxProps, "onChange"> | SvgIconProps>}
        />
    if (type === 'array') {
        return <PrettyArray
            nest_level={nest_level + 1}
            edit_mode={edit_mode}
            target={value}
            onEdit={onEdit}
            child_type={lock_child_type_to}
        />
    }
    if (type === 'object') {
        return <PrettyObject
            nest_level={nest_level + 1}
            edit_mode={edit_mode}
            onEdit={onEdit}
            target={value}
        />
    }
    if (is_lookup_key(type)) {
        return <PrettyResource
            value={value}
            onChange={(v) => onEdit && onEdit(v)}
            edit_mode={edit_mode}
            lookup_key={type}
            {...childProps as Partial<ChipProps>}
        />
    }

    console.error(
        "Prettify failure",
        {target, nest_level, edit_mode, onEdit, lock_type_to, lock_child_type_to, inferred_type: type, ...childProps}
    )
    throw new Error(`Could not prettify value: ${value}`)
}

export default function Prettify(
    {hide_type_changer, ...props}: PrettifyProps &
        Partial<TextFieldProps | TypographyProps | Omit<CheckboxProps, "onChange"> | SvgIconProps>
) {
    props.nest_level = props.nest_level ?? 0
    props.edit_mode = props.edit_mode ?? false
    const pretty = <Pretty {...props} />
    return props.edit_mode && props.onEdit && !hide_type_changer?
        <TypeChangeWrapper
            onTypeChange={props.onEdit}
            currentValue={props.target}
            lock_type={props.lock_type_to ?? false}
        >
            {pretty}
        </TypeChangeWrapper> :
        pretty
}