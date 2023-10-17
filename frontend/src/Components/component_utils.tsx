import Stack from "@mui/material/Stack";
import CountBadge from "./CountBadge";
import {ICONS} from "../icons";
import {PATHS} from "../App";
import Tooltip from "@mui/material/Tooltip";
import IconButton from "@mui/material/IconButton";
import {Link} from "react-router-dom";
import EditIcon from "@mui/icons-material/Edit";
import ManageSearchIcon from "@mui/icons-material/ManageSearch";
import RemoveIcon from "@mui/icons-material/Remove";
import AddIcon from "@mui/icons-material/Add";
import React, {ReactNode, useEffect, useState} from "react";
import Typography from "@mui/material/Typography";
import Grid, {Grid2Props} from "@mui/material/Unstable_Grid2";
import clsx from "clsx";
import useStyles from "../UseStyles";
import CheckIcon from "@mui/icons-material/Check";
import ClearIcon from "@mui/icons-material/Clear";
import TableContainer, {TableContainerProps} from "@mui/material/TableContainer";
import Paper from "@mui/material/Paper";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Table from "@mui/material/Table";
import Card from "@mui/material/Card";
import ListItem from "@mui/material/ListItem";
import List from "@mui/material/List";
import Box from "@mui/material/Box";
import SaveIcon from "@mui/icons-material/Save";
import CloseIcon from "@mui/icons-material/Close";
import UndoIcon from "@mui/icons-material/Undo";
import RedoIcon from "@mui/icons-material/Redo";
import TextField from "@mui/material/TextField";
import {useDebouncedCallback} from "use-debounce";
import ToggleButtonGroup, {ToggleButtonGroupProps} from "@mui/material/ToggleButtonGroup";
import ToggleButton from "@mui/material/ToggleButton";
import AbcIcon from "@mui/icons-material/Abc";
import NumbersIcon from "@mui/icons-material/Numbers";
import DataObjectIcon from "@mui/icons-material/DataObject";
import DataArrayIcon from "@mui/icons-material/DataArray";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";
import Popper from "@mui/material/Popper";

export type ObjectReferenceProps =
    { uuid: string } |
    { id: number } |
    { url: string }

export type ExpandableCardProps = ObjectReferenceProps & {
    expanded?: boolean
    editing?: boolean
}

export function id_from_ref_props<T extends number|string>(props: ObjectReferenceProps|string|number): T {
    if (typeof props === 'number')
        return props as T
    if (typeof props === 'object') {
        if ('uuid' in props) {
            return props.uuid as T
        } else if ('id' in props) {
            return props.id as T
        }
    }
    const url = typeof props === 'string'? props : props.url
    try {
        const id = url.split('/').filter(x => x).pop()
        if (id !== undefined) return id as T
    } catch (e) {
        throw new Error(`Could not parse id from url: ${url}: ${e}`)
    }
    throw new Error(`Could not parse id from url: ${url}`)
}

type CardActionBarProps = {
    type: string
    uuid?: string
    path?: string
    family_uuid?: string
    cycler_test_count?: number | undefined
    editable?: boolean
    editing?: boolean
    setEditing?: (editing: boolean) => void
    onEditSave?: () => boolean
    onEditDiscard?: () => boolean
    undoable?: boolean
    redoable?: boolean
    onUndo?: () => void
    onRedo?: () => void
    destroyable?: boolean
    expanded?: boolean
    setExpanded?: (expanded: boolean) => void
}

/**
 *
 * @param props.onEditSave function that returns true if the save was successful. If false, the editing state will not change.
 * @param props.onEditDiscard function that returns true if the discard was successful. If false, the editing state will not change.
 *
 * @constructor
 */
export function CardActionBar(props: CardActionBarProps) {
    const typeName = props.type.charAt(0).toUpperCase() + props.type.slice(1)

    let edit_section: ReactNode
    if (props.editable) {
        if (typeof props.setEditing !== 'function')
            throw new Error(`setEditing must be a function if editable=true`)
        if (typeof props.onEditSave !== 'function')
            throw new Error(`onEditSave must be a function if editable=true`)
        if (typeof props.onEditDiscard !== 'function')
            throw new Error(`onEditDiscard must be a function if editable=true`)
        if (!props.editing) {
            edit_section = <Tooltip title={`Edit this ${typeName}`} arrow describeChild key="edit">
                <IconButton onClick={() => props.setEditing!(true)}>
                    <EditIcon fontSize="large"/>
                </IconButton>
            </Tooltip>
        } else {
            if (props.undoable && typeof props.onUndo !== 'function')
                throw new Error(`onUndo must be a function if undoable=true`)
            if (props.redoable && typeof props.onRedo !== 'function')
                throw new Error(`onRedo must be a function if redoable=true`)
            const undo_buttons = <>
                {props.onUndo && <Tooltip title={`Undo`} arrow describeChild key="undo">
                <span>
                <IconButton onClick={props.onUndo!} disabled={!props.undoable}>
                    <UndoIcon fontSize="large"/>
                </IconButton>
                </span>
                </Tooltip>}
                {props.onRedo && <Tooltip title={`Redo`} arrow describeChild key="redo">
                    <span>
                    <IconButton onClick={props.onRedo!} disabled={!props.redoable}>
                        <RedoIcon fontSize="large"/>
                    </IconButton>
                    </span>
                </Tooltip>}
            </>

            edit_section = <>
                <Tooltip title={`Save changes`} arrow describeChild key="save">
                    <IconButton onClick={() => {
                        if (props.onEditSave!())
                            props.setEditing!(false)
                    }}>
                        <SaveIcon fontSize="large" color="success"/>
                    </IconButton>
                </Tooltip>
                {undo_buttons}
                <Tooltip title={`Discard changes`} arrow describeChild key="discard">
                    <IconButton onClick={() => {
                        if (props.onEditDiscard!())
                            props.setEditing!(false)
                    }}>
                        <CloseIcon fontSize="large" color="error"/>
                    </IconButton>
                </Tooltip>
            </>
        }
    }

    return <Stack direction="row" spacing={1} alignItems="center">
        {props.cycler_test_count && <CountBadge
            key={`cycler_tests`}
            icon={<ICONS.CYCLER_TESTS fontSize="large"/>}
            badgeContent={props.cycler_test_count}
            url={`${PATHS.CYCLER_TESTS}?${props.type}=${props.uuid}`}
            tooltip={`Cycler Tests involving this ${typeName}`}
        />}
        {props.editable && edit_section}
        {props.destroyable && <Tooltip title={`Delete this ${typeName}`} arrow describeChild key="delete">
            <IconButton component={Link} to={`${props.path}/${props.uuid}/delete`}>
                <EditIcon fontSize="large"/>
            </IconButton>
        </Tooltip>}
        <Tooltip title={`Go to ${typeName} Page`} arrow describeChild key="goto">
            <IconButton component={Link} to={`${props.path}/${props.uuid}`}>
                <ManageSearchIcon fontSize="large" />
            </IconButton>
        </Tooltip>
        {props.family_uuid? <Tooltip title={`Go to ${typeName} Family Page`} arrow describeChild key="family">
                <IconButton component={Link} to={`${props.path}_families/${props.family_uuid}`}>
                    <ICONS.FAMILY fontSize="large" />
                </IconButton>
            </Tooltip> :
            <IconButton disabled={true}>
                <ICONS.FAMILY fontSize="large" />
            </IconButton>}
        {props.expanded !== undefined &&
            props.setExpanded !== undefined &&
            <Tooltip title={props.expanded ? "Hide Details" : "Show Details"} arrow describeChild key="expand">
                <IconButton onClick={() => props.setExpanded!(!props.expanded)}>
                    {props.expanded ? <RemoveIcon fontSize="large" /> : <AddIcon fontSize="large" />}
                </IconButton>
            </Tooltip>}
    </Stack>
}

type PrettyObjectProps = {
    object: {[key: string]: any}
    exclude_keys?: string[]
    type_locked_keys?: string[]
    nest_level?: number
    edit_mode?: boolean
    onEdit?: (value: { [key: string]: any }) => void
}
export function PrettyObject(props: PrettyObjectProps & TableContainerProps) {
    const [focusElement, setFocusElement] = useState<HTMLElement | null>(null)
    const [focusKey, setFocusKey] = useState<string | null>(null)
    const edit_mode = props.edit_mode || false
    const edit_fun_factory = props.onEdit?
        (k: string) => (v: Partial<object>) => props.onEdit!({...props.object, [k]: v}) :
        (k: string) => (() => {})
    const nest_level = props.nest_level || 0
    const table_props = {...props}
    delete table_props.edit_mode
    delete table_props.onEdit
    delete table_props.nest_level
    const {classes} = useStyles()
    const exclude_keys = props.exclude_keys || ['url']
    const keys = Object.keys(props.object).filter(key => !exclude_keys.includes(key))
    if (keys.length === 0) return <></>
    const obj: {[key: string]: ReactNode} = {}
    keys.forEach(key => {
        const v: any = props.object[key]
        if (v === null || v === undefined) return
        obj[key] = <Prettify nest_level={nest_level} edit_mode={edit_mode} onEdit={edit_fun_factory(key)} target={v} />
    })
    return <TableContainer
        className={clsx(classes.pretty_table, {[classes.pretty_table_nested]: nest_level % 2})}
        {...table_props as TableContainerProps}
    >
        <Table size="small">
            <TableBody>
                {Object.entries(obj).map(([key, value], i) => (
                    <TableRow
                        onFocus={(e) => {
                            setFocusElement(e.currentTarget)
                            setFocusKey(key)
                        }}
                        onBlur={(e) => {
                            if (focusKey === key) {
                                setFocusElement(null)
                                setFocusKey(null)
                            }
                        }}
                        key={i}
                    >
                        <TableCell component="th" scope="row" key={`key_${i}`} align="right">
                            <Stack>
                                {edit_mode && !props.type_locked_keys?.includes(key)?
                                    <Prettify
                                        nest_level={nest_level}
                                        edit_mode={edit_mode}
                                        onEdit={(new_key: string) => {
                                            const new_obj = {...props.object}
                                            if (new_key !== "")
                                                new_obj[new_key] = props.object[new_key]
                                            delete new_obj[key]
                                            props.onEdit!(new_obj)
                                        }}
                                        target={key}
                                    /> :
                                    <Typography key={`name_${i}`} variant="subtitle2" component="span" textAlign="right">
                                        {key}
                                    </Typography>
                                }
                                {edit_mode &&
                                    <Popper
                                        open={key === focusKey}
                                        anchorEl={focusElement}
                                        placement="top"
                                    >
                                        <Stack direction="row" spacing={0.5} key={`typechanger_${i}`}>
                                            <TypeChanger
                                                key={`typechanger_${i}`}
                                                currentValue={props.object[key]}
                                                onTypeChange={edit_fun_factory(key)}
                                                disabled={props.type_locked_keys?.includes(key) || false}
                                            />
                                            <Tooltip title={`Remove ${key}`} arrow describeChild key={`remove_${i}`}>
                                <span>
                                    <IconButton
                                        onClick={() => {
                                            const new_obj = {...props.object}
                                            delete new_obj[key]
                                            props.onEdit!(new_obj)
                                        }}
                                        disabled={props.type_locked_keys?.includes(key) || false}
                                    >
                                        <ClearIcon />
                                    </IconButton>
                                </span>
                                            </Tooltip>
                                        </Stack>
                                    </Popper>
                                }
                            </Stack>
                        </TableCell>
                        <TableCell width="100%" key={`value_${i}`} align="left">{value}</TableCell>
                    </TableRow>))}
            </TableBody>
        </Table>
    </TableContainer>
}

type PrettifyProps = {
    target: any
    nest_level: number
    edit_mode: boolean
    onEdit?: (value: any) => void
}

function Prettify(props: PrettifyProps) {
    const [value, setValue] = useState<any>(props.target)
    useEffect(() => {
        setValue(props.target)
    }, [props.target])
    const debounced = useDebouncedCallback(
        props.onEdit? (value: any) => props.onEdit!(value) : (v: any) => {},
        500
    )
    if (props.edit_mode && typeof props.onEdit !== 'function')
        throw new Error(`onEdit must be a function if edit_mode=true`)
    if (value === null || value === undefined) return <></>
    if (typeof value === 'string')
        return props.edit_mode?
            <TextField
                onChange={(e) => {
                    setValue(e.target.value)
                    debounced(e.target.value)
                }}
                variant="standard"
                value={value}
            /> :
            <Typography component="span" variant="body1">{value}</Typography>
    if (typeof value === 'number')
        return <Typography component="span" variant="overline" sx={{fontSize: "1.1em"}}>{value}</Typography>
    if (typeof value === 'boolean')
        return value? <CheckIcon /> : <ClearIcon />
    if (value instanceof Array) {
        return <List dense={true}>
            {value.map((v: any, i: number) => <ListItem key={i}>
                <Prettify nest_level={props.nest_level} edit_mode={props.edit_mode} onEdit={props.onEdit} target={v} />
            </ListItem>)}
        </List>
    }
    if (typeof value === 'object') {
        return <PrettyObject
            nest_level={props.nest_level + 1}
            edit_mode={props.edit_mode}
            onEdit={props.onEdit}
            object={value}
        />
    }
    console.error("Prettify failure", props)
    throw new Error(`Could not prettify value: ${value}`)
}

type TypeChangerProps = {
    currentValue: any
    onTypeChange: (newValue: any) => void
    disabled: boolean
}

function TypeChanger(props: TypeChangerProps) {
    const str = (v: any) => {
        try {
            return `${v}`
        } catch(e) {
            console.warn(`Could not stringify value: ${v}`, e)
            return ""
        }
    }
    const num = (v: any) => {
        try {
            return parseInt(v)
        } catch (e_int) {
            try {
                return parseFloat(v)
            } catch (e) {
                console.warn(`Could not numerify value: ${v}`, e, e_int)
                return 0
            }
        }
    }

    const obj = (v: any) => {
        try {
            if (typeof v === 'string')
                return JSON.parse(v)
            if (v instanceof Array) {
                const o: {[key: number]: any} = {}
                v.forEach((vv, i) => o[i] = vv)
            }
            return {0: v}
        } catch (e) {
            console.warn(`Could not objectify value: ${v}`, e)
            return {0: v}
        }
    }

    const arr = (v: any) => {
        try {
            if (typeof v === 'string')
                return JSON.parse(v)
            return [v]
        } catch (e) {
            console.warn(`Could not arrayify value: ${v}`, e)
            return [v]
        }
    }

    const get_conversion_fun = (type: string) => {
        switch (type) {
            case 'string': return str
            case 'number': return num
            case 'boolean': return (v: any) => !!v
            case 'object': return obj
            case 'array': return arr
        }
        return (v: any) => undefined
    }
    const [value, _setValue] = useState(props.currentValue instanceof Array? 'array' : typeof props.currentValue)
    useEffect(() => {
        _setValue(props.currentValue instanceof Array? 'array' : typeof props.currentValue)
    }, [props.currentValue])
    const debounced = useDebouncedCallback(() => {
        const converter = get_conversion_fun(value)
        const newValue = converter(props.currentValue)
        props.onTypeChange(newValue)
    }, 500)
    const change = (v: any) => {
        _setValue(v)
        debounced()
    }

    return <Tooltip
        key="string"
        title={props.disabled?
            `This variable must always be ${value}` :
            "Change the type of this variable [string, number, boolean, object, array]"}
        arrow
        describeChild
    >
        <ToggleButtonGroup
            size="small"
            exclusive
            value={value}
            onChange={(e, v) => change(v)}
        >
            <ToggleButton
                value="string"
                disabled={value === 'string' || props.disabled}
                selected={value === 'string'}
            >
                <AbcIcon />
            </ToggleButton>
            <ToggleButton
                value="number"
                disabled={value === 'number' || props.disabled}
                selected={value === 'number'}
            >
                <NumbersIcon />
            </ToggleButton>
            <ToggleButton
                value="boolean"
                disabled={value === 'boolean' || props.disabled}
                selected={value === 'boolean'}
            >
                <PowerSettingsNewIcon />
            </ToggleButton>
            <ToggleButton
                value="object"
                disabled={value === 'object' || props.disabled}
                selected={value === 'object'}
            >
                <DataObjectIcon />
            </ToggleButton>
            <ToggleButton
                value="array"
                disabled={value === 'array' || props.disabled}
                selected={value === 'array'}
            >
                <DataArrayIcon />
            </ToggleButton>
        </ToggleButtonGroup>
    </Tooltip>
}
