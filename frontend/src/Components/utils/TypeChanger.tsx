import Tooltip from "@mui/material/Tooltip";
import React, {
    ReactNode,
    useEffect,
    useState
} from "react";
import {useDebouncedCallback} from "use-debounce";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import ToggleButton from "@mui/material/ToggleButton";
import AbcIcon from "@mui/icons-material/Abc";
import NumbersIcon from "@mui/icons-material/Numbers";
import DataObjectIcon from "@mui/icons-material/DataObject";
import DataArrayIcon from "@mui/icons-material/DataArray";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";
import {PopoverProps} from "@mui/material";
import SvgIcon from "@mui/material/SvgIcon";
import IconButton from "@mui/material/IconButton";
import Popover from "@mui/material/Popover";
import clsx from "clsx";
import useStyles from "../../UseStyles";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";

const str = (v: any) => {
    try {return JSON.stringify(v)} catch(e) {
        console.warn(`Could not stringify value: ${v}`, e)
        return ""
    }
}
const num = (v: any) => {
    const n = Number(v)
    if (isNaN(n)) {
        console.warn(`Could not numberify value: ${v}`)
        return 0
    }
    return n
}
const obj = (v: any) => {
    try {
        if (v instanceof Array) {
            const o: {[key: number]: any} = {}
            v.forEach((vv, i) => o[i] = vv)
            return o
        }
        if (v instanceof Object) return v
        if (typeof v === 'string' && (v.startsWith('{') && v.endsWith('}')))
            return JSON.parse(v)
    } catch (e) {
        console.warn(`Could not objectify value: ${v}`, e)
    }
    return {0: v}
}
const arr = (v: any) => {
    try {
        if (v instanceof Array) return v
        if (typeof v === 'object') return Object.values(v)
        if (typeof v === 'string' && (v.startsWith('[') && v.endsWith(']')))
            return JSON.parse(v)
    } catch (e) {
        console.warn(`Could not arrayify value: ${v}`, e)
    }
    return [v]
}

const type_map: {[key: string]: {icon: typeof SvgIcon, tooltip: ReactNode}} = {
    string: {
        icon: AbcIcon,
        tooltip: "String"
    },
    number: {
        icon: NumbersIcon,
        tooltip: "Number"
    },
    boolean: {
        icon: PowerSettingsNewIcon,
        tooltip: "Boolean"
    },
    object: {
        icon: DataObjectIcon,
        tooltip: "Object (JSON strings will be parsed)"
    },
    array: {
        icon: DataArrayIcon,
        tooltip: "Array (JSON strings will be parsed)"
    }
}

export type TypeChangerSupportedType =
    string |
    number |
    boolean |
    {[key: string]: TypeChangerSupportedType} |
    TypeChangerSupportedType[]

type TypeChangerSupportedTypeName = keyof typeof type_map & string

export type TypeChangerProps = {
    currentValue: TypeChangerSupportedType
    onTypeChange: (newValue: TypeChangerSupportedType) => void
    disabled: boolean
}

export type TypeChangerPopoverProps = {
    value: TypeChangerSupportedTypeName
    onTypeChange: (newValue: TypeChangerSupportedTypeName) => void
} & PopoverProps

function TypeChangePopover({value, onTypeChange, ...props}: TypeChangerPopoverProps) {
    const {classes} = useStyles()
    return <Popover className={clsx(classes.type_changer_popover)} {...props}>
        <ToggleButtonGroup
            size="small"
            exclusive
            value={value}
            onChange={(_, v: TypeChangerSupportedTypeName) => onTypeChange(v)}
        >
            {Object.entries(type_map).map(([type, ICON]) =>
                <ToggleButton value={type} key={type} selected={value === type} disabled={value === type}>
                    <Tooltip title={ICON.tooltip} arrow placement="bottom" describeChild={true}>
                        <ICON.icon />
                    </Tooltip>
                </ToggleButton>)}
        </ToggleButtonGroup>
    </Popover>
}

export default function TypeChanger(
    {currentValue, onTypeChange, disabled, ...props}: TypeChangerProps & TypeChangerPopoverProps
) {
    const {classes} = useStyles()

    const get_conversion_fun = (type: string) => {
        switch (type) {
            case 'string': return str
            case 'number': return num
            case 'boolean': return (v: any) => !!v
            case 'object': return obj
            case 'array': return arr
        }
        console.warn(`Could not find conversion function for type: ${type}, defaulting to empty string`)
        return () => ""
    }
    const get_type_name = (value: TypeChangerSupportedType) => {
        return (value instanceof Array? 'array' : typeof value) as TypeChangerSupportedTypeName
    }

    const [value, _setValue] =
        useState<TypeChangerSupportedTypeName>(get_type_name(currentValue))
    const [popoverAnchor, setPopoverAnchor] = useState<HTMLElement|null>(null)

    useEffect(() => _setValue(get_type_name(currentValue)), [currentValue])

    return <Tooltip
        key="string"
        title={disabled? value : <Stack justifyItems="center" alignContent="center">
                <Typography textAlign="center" variant="caption">{value}</Typography>
                <Typography textAlign="center" variant="caption">click to change type</Typography>
            </Stack>}
        arrow
        describeChild
        placement="top"
    >
        <span>
            <TypeChangePopover
                {...props}
                onTypeChange={(t) => {
                    setPopoverAnchor(null)
                    return onTypeChange(get_conversion_fun(t)(currentValue))
                }}
                value={value as TypeChangerSupportedTypeName}
                open={!!popoverAnchor}
                anchorEl={popoverAnchor}
                onClose={() => setPopoverAnchor(null)}
            />
            <IconButton
                onClick={(e) => setPopoverAnchor(e.currentTarget || null)}
                disabled={disabled}
                className={clsx(classes.type_changer_button)}
            >
                {React.createElement(type_map[value as TypeChangerSupportedTypeName].icon)}
            </IconButton>
        </span>
    </Tooltip>
}
