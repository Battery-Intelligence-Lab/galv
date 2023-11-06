import React, {Fragment, useContext, useState} from "react";
import Stack from "@mui/material/Stack";
import {Serializable} from "../utils/TypeChanger";
import Chip, {ChipProps} from "@mui/material/Chip";
import Tooltip from "@mui/material/Tooltip";
import {
    Filter,
    FILTER_FUNCTIONS,
    FILTER_MODES,
    FilterContext,
    FilterFamily,
    FilterMode
} from "./FilterContext";
import {DISPLAY_NAMES_PLURAL, Field, FIELDS, ICONS, is_lookup_key, LookupKey} from "../../constants";
import Grid from "@mui/material/Unstable_Grid2";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import ToggleButton from "@mui/material/ToggleButton";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import TextField from "@mui/material/TextField";
import Autocomplete from "@mui/material/Autocomplete";
import Typography from "@mui/material/Typography";
import IconButton from "@mui/material/IconButton";
import clsx from "clsx";
import useStyles from "../../UseStyles";
import {ButtonGroup} from "@mui/material";

type FilterChipProps = {
    filter: Filter
}

function FilterChip({filter, ...chipProps}: FilterChipProps & ChipProps) {
    return <Tooltip title={filter.family.get_name(filter, false)}>
        <Chip size="small" label={filter.family.get_name(filter, true)} {...chipProps}/>
    </Tooltip>
}

type FilterCreateFormProps = {
    onCreate: (lookup_key: LookupKey, filter: Filter) => void
    onCancel?: () => void
}

const isFilterableField = (field: Field) => ["string", "number"].includes(field.type)

function FilterCreateForm({onCreate, onCancel}: FilterCreateFormProps) {
    const [value, setValue] = useState<Serializable>("")
    const [key, setKey] = useState<string>("")
    const [lookupKey, setLookupKey] =
        useState<LookupKey>(Object.keys(FIELDS)[0] as LookupKey)
    const [family, setFamily] = useState<FilterFamily|"">("")

    const reset = () => {
        setValue("")
        setKey("")
        setFamily("")
        setLookupKey(Object.keys(FIELDS)[0] as LookupKey)
    }

    const is_family_appropriate = (family: FilterFamily, key: string): boolean => {
        const field = FIELDS[lookupKey]
        const k = key as keyof typeof field
        if (!field || !field[k]) return true
        const field_info = field[k] as Field

        return family.applies_to.includes(field_info.type as any)
    }

    return <Stack className={clsx("create_form")} spacing={0.5}>
        <Stack direction="row" spacing={0.5} key="properties" className={clsx('properties')}>
            <Select
                value={lookupKey}
                onChange={(e) =>
                    is_lookup_key(e.target.value) && setLookupKey(e.target.value)}
                autoWidth
                label="Filter"
                size="small"
            >
                <MenuItem key='none' value="" disabled />
                {Object.keys(FIELDS).map((lookup_key) => {
                    const ICON = ICONS[lookup_key as LookupKey]
                    return <MenuItem value={lookup_key as LookupKey} key={lookup_key}>
                        <Tooltip title={DISPLAY_NAMES_PLURAL[lookup_key as LookupKey]} describeChild={true}>
                            <ICON fontSize="small"/>
                        </Tooltip>
                    </MenuItem>
                })}
            </Select>
            <Autocomplete
                key="key"
                freeSolo
                options={
                    Object.entries(FIELDS[lookupKey])
                        .filter(([k, v]) => isFilterableField(v))
                        .map(([k, _]) => k)
                }
                renderInput={(params) => <TextField {...params} label="X" />}
                onChange={(_, v) => setKey(v || "")}
                size="small"
                sx={{minWidth: (t) => t.spacing(20)}}
            />
            <Select
                key="family"
                value={family === ""? "" : FILTER_FUNCTIONS.findIndex(f => f === family)}
                onChange={(e, v) => {
                    try {
                        setFamily(FILTER_FUNCTIONS[Number(e.target.value)])
                    } catch {
                        setFamily("")
                    }
                }}
                autoWidth
                label="Using"
                size="small"
                sx={{minWidth: (t) => t.spacing(20)}}
            >
                <MenuItem key='none' value="" disabled />
                {FILTER_FUNCTIONS.map((family, i) => <MenuItem
                    key={i}
                    value={i}
                    disabled={!is_family_appropriate(family, key)}
                >
                    {family.name}
                </MenuItem>)}
            </Select>
            <TextField
                size="small"
                key="value"
                value={value}
                onChange={(e) => setValue(e.currentTarget.value || "")}
                label="Y"
            />
        </Stack>
        <Stack direction="row" spacing={0.5} key="summary" className={clsx('summary')}>
            <Typography key="summary" className={clsx('summary-text')}>
                {family !== "" && family.get_name({key: key || 'X', test_versus: value || 'Y', family}, false)}
            </Typography>
            <ButtonGroup>
                <IconButton key="create" onClick={() => {
                    if (family === "" || value === "" || key === "") return
                    onCreate(lookupKey, {key, family, test_versus: value})
                    reset()
                }} >
                    <ICONS.CREATE fontSize="small" />
                </IconButton>
                <IconButton key="cancel" onClick={() => {onCancel && onCancel(); reset()}} >
                    <ICONS.CANCEL fontSize="small" />
                </IconButton>
            </ButtonGroup>
        </Stack>
    </Stack>
}

export default function FilterBar() {

    const {activeFilters, setActiveFilters} = useContext(FilterContext)
    const [creating, setCreating] = useState<boolean>(true)

    const {classes} = useStyles()

    return <Grid container key="filter_bar_content" className={clsx(classes.filter_bar)}>
        <Stack spacing={1} key="existing_filters" className={clsx("existing_filters")}>
            {
                Object.entries(activeFilters).map(([lookup_key, content]) => {
                    const _key = lookup_key as LookupKey
                    const ICON = ICONS[_key]
                    if (content.filters.length === 0) return <Fragment key={_key}></Fragment>
                    return <Stack direction="row" spacing={1} key={_key} className={clsx("horizontal")}>
                        <ICON key='icon' fontSize="small" />
                        <ToggleButtonGroup
                            key='mode'
                            value={content.mode}
                            exclusive
                            onChange={(_, v) => setActiveFilters({
                                ...activeFilters,
                                [_key]: {...content, mode: v as FilterMode}
                            })}
                            aria-label="Filter mode"
                            size="small"
                        >
                            <ToggleButton key={'any'} value={FILTER_MODES.ANY}>{FILTER_MODES.ANY}</ToggleButton>
                            <ToggleButton key={'all'} value={FILTER_MODES.ALL}>{FILTER_MODES.ALL}</ToggleButton>
                        </ToggleButtonGroup>
                        {content.filters.map((filter, i) =>
                            <FilterChip
                                key={`filter_${_key}-${i}`}
                                filter={filter}
                                onDelete={() => setActiveFilters({
                                    ...activeFilters,
                                    [_key]: {...content, filters: content.filters.filter(f => f !== filter)}
                                })}
                            />
                        )}
                    </Stack>
                })
            }
        </Stack>
        {
            creating?
                <FilterCreateForm
                    key="create_form"
                    onCreate={(lookup_key, filter) => {
                        console.log(`creating filter`, {lookup_key, filter})
                        setActiveFilters({
                            ...activeFilters,
                            [lookup_key]: {
                                mode: activeFilters[lookup_key].mode ?? FILTER_MODES.ALL,
                                filters: [...activeFilters[lookup_key].filters, filter]
                            }
                        })
                    }}
                    onCancel={() => setCreating(false)}
                /> :
                <Chip
                    key='new_filter'
                    className={clsx("new_filter")}
                    icon={<ICONS.CREATE fontSize="small"/>}
                    label="New filter"
                    onClick={() => setCreating(true)}
                />
        }
    </Grid>
}