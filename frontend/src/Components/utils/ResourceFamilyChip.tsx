import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {usePropParamId} from "./misc";
import LoadingChip from "../utils/LoadingChip";
import QueryWrapper from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {
    API_HANDLERS,
    CHILD_PROPERTY_NAMES,
    DISPLAY_NAMES,
    FILTER_NAMES, GET_REPRESENTATIONS,
    PATHS, ICONS, API_SLUGS
} from "../../constants";
import {Family} from "./ResourceCard";

type ResourceFamilyChipProps = {
    uuid: string
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof DISPLAY_NAMES &
        keyof typeof FILTER_NAMES &
        keyof typeof CHILD_PROPERTY_NAMES &
        keyof typeof API_HANDLERS &
        keyof typeof GET_REPRESENTATIONS &
        string
}

export default function ResourceFamilyChip<T extends Family>(
    {uuid, lookup_key, ...chipProps}: ResourceFamilyChipProps & ChipProps
) {
    const { classes } = useStyles();

    const _uuid = usePropParamId<string>(uuid)
    const api_handler = new API_HANDLERS[lookup_key]()
    // TODO May need to turn this into a function to avoid losing the binding to api_handler as 'this'
    const api_get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, _uuid],
        // @ts-ignore
        queryFn: () => api_handler[`${API_SLUGS[lookup_key]}Retrieve`](_uuid)
    })

    const ICON = ICONS[lookup_key]

    return <QueryWrapper
        queries={[query]}
        loading={<LoadingChip url={`/${PATHS[lookup_key]}/${_uuid}`} icon={<ICON/>} {...chipProps}/>}
        error={(queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS[lookup_key]}/${_uuid}`}
            detail={queries[0].error?.response?.data?.toString()}
            key={_uuid}
            icon={<ICON />}
            variant="outlined"
        />
        }
        success={<Chip
            key={_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICON />}
            variant="outlined"
            label={query.data?.data? GET_REPRESENTATIONS[lookup_key](query.data?.data) : ""}
            clickable={true}
            component={Link}
            to={`${PATHS[lookup_key]}/${_uuid}`}
            {...chipProps as ChipProps as any}
        />}
    />

}