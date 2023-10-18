import Tooltip from "@mui/material/Tooltip";
import React, {useEffect, useState} from "react";
import {useDebouncedCallback} from "use-debounce";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import ToggleButton from "@mui/material/ToggleButton";
import AbcIcon from "@mui/icons-material/Abc";
import NumbersIcon from "@mui/icons-material/Numbers";
import DataObjectIcon from "@mui/icons-material/DataObject";
import DataArrayIcon from "@mui/icons-material/DataArray";
import PowerSettingsNewIcon from "@mui/icons-material/PowerSettingsNew";

type TypeChangerProps = {
    currentValue: any
    onTypeChange: (newValue: any) => void
    disabled: boolean
}

export default function TypeChanger(props: TypeChangerProps) {
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
            if (v instanceof Object) return v
            if (typeof v === 'string' && (v.startsWith('{') && v.endsWith('}')))
                return JSON.parse(v)
            if (v instanceof Array) {
                const o: {[key: number]: any} = {}
                v.forEach((vv, i) => o[i] = vv)
            }
        } catch (e) {
            console.warn(`Could not objectify value: ${v}`, e)
        }
        return {0: v}
    }
    const arr = (v: any) => {
        try {
            if (v instanceof Array) return v
            if (typeof v === 'string' && (v.startsWith('[') && v.endsWith(']')))
                return JSON.parse(v)
        } catch (e) {
            console.warn(`Could not arrayify value: ${v}`, e)
        }
        return [v]
    }

    const get_conversion_fun = (type: string) => {
        switch (type) {
            case 'string': return str
            case 'number': return num
            case 'boolean': return (v: any) => !!v
            case 'object': return obj
            case 'array': return arr
        }
        return () => undefined
    }
    const [value, _setValue] = useState(props.currentValue instanceof Array? 'array' : typeof props.currentValue)
    useEffect(() => {
        _setValue(props.currentValue instanceof Array? 'array' : typeof props.currentValue)
    }, [props.currentValue])
    const debounced = useDebouncedCallback((v: any) => {
        const converter = get_conversion_fun(v)
        const newValue = converter(props.currentValue)
        props.onTypeChange(newValue)
    }, 500)
    const change = (v: string) => {
        _setValue(v)
        debounced(v)
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
            onChange={(_, v: string) => change(v)}
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
