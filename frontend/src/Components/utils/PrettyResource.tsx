import {API_HANDLERS, API_SLUGS, DISPLAY_NAMES, FAMILY_LOOKUP_KEYS, GET_REPRESENTATIONS} from "../../constants";
import {ChipProps} from "@mui/material/Chip";
import React, {useEffect, useState} from "react";
import useStyles from "../../UseStyles";
import {AxiosError, AxiosResponse} from "axios";
import {build_placeholder_url, get_url_components, PaginatedAPIResponse} from "./misc";
import {useQuery} from "@tanstack/react-query";
import TextField from "@mui/material/TextField";
import clsx from "clsx";
import ButtonBase from "@mui/material/ButtonBase";
import ResourceChip from "./ResourceChip";
import {PrettyComponentProps, PrettyString} from "./Prettify";
import Autocomplete, {createFilterOptions} from "@mui/material/Autocomplete";
import CircularProgress from "@mui/material/CircularProgress";
import {CreateFilterOptionsConfig} from "@mui/material";

export const PrettyResourceSelect = (
    {value, onChange, edit_mode, lookup_key, resource_id, ...childProps}:
        { lookup_key: keyof typeof API_HANDLERS, resource_id: string } & PrettyComponentProps & Partial<ChipProps>
) => {
    console.log(`PrettySelect`, {value, onChange, edit_mode, lookup_key, resource_id: resource_id, childProps})

    const api_handler = new API_HANDLERS[lookup_key]()
    const api_list = api_handler[
        `${API_SLUGS[lookup_key]}List` as keyof typeof api_handler
        ] as () => Promise<AxiosResponse<PaginatedAPIResponse>>
    const query = useQuery<AxiosResponse<PaginatedAPIResponse>, AxiosError>({
        queryKey: [lookup_key, 'list'],
        queryFn: () => api_list.bind(api_handler)()
    })

    const family_lookup_key = Object.keys(FAMILY_LOOKUP_KEYS).includes(lookup_key)?
        FAMILY_LOOKUP_KEYS[lookup_key as keyof typeof FAMILY_LOOKUP_KEYS] : undefined
    const family_api_handler = family_lookup_key?
        new API_HANDLERS[family_lookup_key as keyof typeof API_HANDLERS]() : null
    const family_api_list = family_api_handler !== null?
        family_api_handler[
            `${API_SLUGS[family_lookup_key as keyof typeof API_SLUGS]}List` as keyof typeof family_api_handler
            ] as () => Promise<AxiosResponse<PaginatedAPIResponse>> :
        () => Promise.resolve(null)
    const family_queryFn = family_api_handler !== null?
        () => family_api_list.bind(family_api_handler)() :
        () => Promise.resolve(null)
    const family_query = useQuery<AxiosResponse<PaginatedAPIResponse>|null, AxiosError>({
        queryKey: [family_lookup_key, 'list'],
        queryFn: family_queryFn
    })

    const [url, setUrl] = useState<string>("")
    const [open, setOpen] = React.useState(false);
    const loading = open && query.isLoading;

    useEffect(() => setUrl(value), [value])

    const url_to_query_result = (url: string) => query.data?.data.results.find(o => o.url === url)
    const represent = (url: string) => {
        const object = url_to_query_result(url)
        if (!object) return url
        return GET_REPRESENTATIONS[lookup_key as keyof typeof GET_REPRESENTATIONS](object)
    }
    const url_to_value = (url: string) => represent(url)
    const value_to_url = (value: string) => {
        // console.log(`value_to_url`, {value, url, repr_value: represent(value), repr_url: represent(url)})
        const object = query.data?.data.results.find(o => represent(o.url) === value)
        return object?.url || value
    }

    const {classes} = useStyles()

    return <Autocomplete
        className={clsx(classes.pretty_select)}
        freeSolo={true}
        filterOptions={createFilterOptions({stringify: represent} as CreateFilterOptionsConfig<any>)}
        open={open}
        onOpen={() => setOpen(true)}
        onChange={(e, v) => {
            // console.log(`onChange`, {e, v, value, url})
            if (value_to_url(v || "") !== url) {
                const new_url = value_to_url(v || "")
                if (get_url_components(new_url))
                    onChange(new_url)
                else
                    onChange(build_placeholder_url(lookup_key, new_url||'new'))
            }
            setOpen(false)
        }}
        onClose={() => setOpen(false)}
        value={url_to_value(url)}
        options={query.data?.data.results.map(r => url_to_value(r.url)) || []}
        loading={loading}
        getOptionLabel={(option: string) => option}
        groupBy={family_lookup_key? (option) => url_to_query_result(value_to_url(option)).family : undefined}
        renderInput={(params) => <TextField
            {...params}
            label={`Select ${DISPLAY_NAMES[lookup_key]}`}
            InputProps={{
                ...params.InputProps,
                endAdornment: (
                    <React.Fragment>
                        {loading ? <CircularProgress color="inherit" size={20}/> : null}
                        {params.InputProps.endAdornment}
                    </React.Fragment>
                ),
            }}
        />
        }
        renderGroup={(params) => <li key={params.key}>
            <div>{
                family_query.data?.data?.results?
                    <ResourceChip
                        resource_id={family_query.data.data.results.find(f => f.url === params.group)}
                        lookup_key={FAMILY_LOOKUP_KEYS[lookup_key as keyof typeof FAMILY_LOOKUP_KEYS]}
                        component={ButtonBase}
                        clickable={false}
                        disabled={true}
                    /> :
                    params.group
            }</div>
            <ul>{params.children}</ul>
        </li>
        }
    />
}

export default function PrettyResource(
    {value, onChange, edit_mode, ...childProps}:
        PrettyComponentProps & Partial<ChipProps & { component: React.ElementType }>
) {
    const url_components = get_url_components(value)
    // console.log(`PrettyResource`, {value, onChange, edit_mode, url_components, childProps})
    const str_representation = <PrettyString value={value} onChange={onChange} {...childProps} edit_mode={false}/>
    if (url_components)
        return edit_mode ?
            <PrettyResourceSelect
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