import React, {PropsWithChildren, SyntheticEvent, useEffect, useState} from "react";
import TextField, {TextFieldProps} from "@mui/material/TextField";
import Typography, {TypographyProps} from "@mui/material/Typography";
import {SvgIconProps} from "@mui/material/SvgIcon"
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import PrettyObject from "./PrettyObject";
import Checkbox, {CheckboxProps} from "@mui/material/Checkbox";
import PrettyArray from "./PrettyArray";
import TypeChanger, {TypeChangerProps, Serializable, detect_type} from "./TypeChanger";
import Stack from "@mui/material/Stack";
import {ChipProps} from "@mui/material/Chip";
import ResourceChip from "./ResourceChip";
import {get_url_components, PaginatedAPIResponse} from "./misc";
import ButtonBase from "@mui/material/ButtonBase";
import {API_HANDLERS, API_SLUGS, DISPLAY_NAMES} from "../../constants";
import MenuItem from "@mui/material/MenuItem";
import {useQuery} from "@tanstack/react-query";
import {AxiosError, AxiosResponse} from "axios";

type PrettifyProps = {
    target: any
    nest_level: number
    edit_mode: boolean
    // onEdit is called when the user leaves the field
    // If it returns a value, the value is set as the new value for the field
    onEdit?: (value: Serializable) => Serializable|void
    allow_type_change?: boolean
    hide_type_changer?: boolean
}

type PrettyComponentProps = {
    value: any
    onChange: (value: any) => void
    edit_mode: boolean
}

export const PrettySelect = (
    {value, onChange, edit_mode, lookup_key, uuid, ...childProps}:
        {lookup_key: keyof typeof API_HANDLERS, uuid: string} & PrettyComponentProps & Partial<ChipProps>
) => {
    console.log(`PrettySelect`, {value, onChange, edit_mode, lookup_key, uuid, childProps})
    const [values, setValues] = useState<any[]>([])
    const api_handler = new API_HANDLERS[lookup_key]()
    const api_list = api_handler[
        `${API_SLUGS[lookup_key]}List` as keyof typeof api_handler
        ] as () => Promise<AxiosResponse<PaginatedAPIResponse>>
    useQuery<AxiosResponse<PaginatedAPIResponse>, AxiosError>({
        queryKey: [lookup_key, 'list'],
        queryFn: () => api_list.bind(api_handler)().then((r: any) => {
            setValues(r.data.results)
            return r
        })
    })
    return <TextField
        select
        label={DISPLAY_NAMES[lookup_key] || "Select"}
        defaultValue={uuid}
        // helperText={`Select a ${DISPLAY_NAMES[lookup_key] || "resource"}`}
        variant="filled"
    >
        {[
            // Override query result that matches the current selection
            ...values.filter((v: any) => v.uuid !== uuid),
            {url: value, uuid: uuid, id: uuid}
        ].map((r: any, i, a) => (
            <MenuItem key={r.url} value={r.uuid || r.id}>
                {<PrettyResource
                    value={r.url}
                    onChange={() => {}} {...childProps}
                    edit_mode={false}
                    component={ButtonBase}
                />}
            </MenuItem>
        ))}
    </TextField>
}

export const PrettyResource = (
    {value, onChange, edit_mode, ...childProps}: PrettyComponentProps & Partial<ChipProps>
) => {
    const url_components = get_url_components(value)
    console.log(`PrettyResource`, {value, onChange, edit_mode, url_components, childProps})
    const str_representation = <PrettyString value={value} onChange={onChange} {...childProps} edit_mode={false} />
    if (url_components)
        return edit_mode?
            <PrettySelect
                {...childProps as ChipProps}
                {...url_components}
                onChange={onChange}
                value={value}
                edit_mode={edit_mode}
            /> :
            <ResourceChip
                {...childProps as ChipProps}
                {...url_components}
                error={str_representation}
            />
    return str_representation
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
    {target, nest_level, edit_mode, onEdit, ...childProps}: PrettifyProps &
        Partial<TextFieldProps | TypographyProps | Omit<CheckboxProps, "onChange"> | SvgIconProps | ChipProps>
) {
    const denull = (t: any) => [null, undefined].includes(t)? '' : t
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

    const type = detect_type(value)

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
    if (Object.keys(API_HANDLERS).includes(type)) {
        return <PrettyResource
            value={value}
            onChange={(v) => onEdit && onEdit(v)}
            edit_mode={edit_mode}
            {...childProps as Partial<ChipProps>}
        />
    }

    console.error("Prettify failure", {target, nest_level, edit_mode, onEdit, ...childProps})
    throw new Error(`Could not prettify value: ${value}`)
}

export default function Prettify(
    {hide_type_changer, allow_type_change, ...props}: PrettifyProps &
        Partial<TextFieldProps | TypographyProps | Omit<CheckboxProps, "onChange"> | SvgIconProps>
) {
    const pretty = <Pretty {...props} />
    return props.edit_mode && props.onEdit && !hide_type_changer?
        <TypeChangeWrapper
            onTypeChange={props.onEdit}
            currentValue={props.target}
            disabled={!allow_type_change}
        >
            {pretty}
        </TypeChangeWrapper> :
        pretty
}