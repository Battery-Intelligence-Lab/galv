import {API_HANDLERS, API_SLUGS, AutocompleteKey} from "../../constants";
import React from "react";
import {AxiosError, AxiosResponse} from "axios";
import {PaginatedAPIResponse} from "../misc";
import {useQuery} from "@tanstack/react-query";
import TextField from "@mui/material/TextField";
import {PrettyComponentProps, PrettyString} from "./Prettify";
import Autocomplete, {AutocompleteProps} from "@mui/material/Autocomplete";
import CircularProgress from "@mui/material/CircularProgress";
import {TypographyProps} from "@mui/material/Typography";
import {AutocompleteResource} from "../ResourceCard";

export default function PrettyAutocomplete(
    {value, onChange, edit_mode, autocomplete_key, ...childProps}:
        {autocomplete_key: AutocompleteKey} &
        PrettyComponentProps &
        (Partial<AutocompleteProps<string, any, true, any>|TypographyProps>)
) {

    const api_handler = new API_HANDLERS[autocomplete_key]()
    const api_list = api_handler[
        `${API_SLUGS[autocomplete_key]}List` as keyof typeof api_handler
        ] as () => Promise<AxiosResponse<PaginatedAPIResponse<AutocompleteResource>>>
    const query = useQuery<AxiosResponse<PaginatedAPIResponse<AutocompleteResource>>, AxiosError>({
        queryKey: ['autocomplete', autocomplete_key, 'list'],
        queryFn: () => api_list.bind(api_handler)()
    })

    if (!edit_mode)
        return <PrettyString
            value={value}
            onChange={onChange}
            {...childProps as Partial<TypographyProps>}
            edit_mode={false}
        />

    return <Autocomplete
        value={value}
        freeSolo
        options={query.data? query.data.data.results.map(r => r.value) : []}
        onChange={(e, value) => onChange(value)}
        renderInput={(params) => (
            <TextField
                {...params}
                label="value"
                InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                        <React.Fragment>
                            {query.isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                            {params.InputProps.endAdornment}
                        </React.Fragment>
                    ),
                }}
            />
        )}
        fullWidth={true}
        {...childProps as Partial<AutocompleteProps<string, any, true, any>>}
    />
}