import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {usePropParamId} from "./misc";
import LoadingChip from "../utils/LoadingChip";
import QueryWrapper, {QueryWrapperProps} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {
    API_HANDLERS,
    DISPLAY_NAMES,
    GET_REPRESENTATIONS,
    PATHS, ICONS, API_SLUGS
} from "../../constants";
import {Family} from "./ResourceCard";

type ResourceFamilyChipProps = {
    uuid: string
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof DISPLAY_NAMES &
        keyof typeof API_HANDLERS &
        string
}

export default function ResourceChip<T extends Family>(
    {uuid, lookup_key, loading, error, success, ...chipProps}:
        ResourceFamilyChipProps & Partial<QueryWrapperProps> & ChipProps
) {
    console.log(`ResourceChip`, {uuid, lookup_key, loading, error, success, chipProps})
    const { classes } = useStyles();

    const _uuid = usePropParamId<string>(uuid)
    const ICON = ICONS[lookup_key]

    const api_handler = new API_HANDLERS[lookup_key]()
    const api_get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, _uuid],
        queryFn: () => api_get.bind(api_handler)(_uuid)
    })


    return <QueryWrapper
        queries={[query]}
        loading={loading || <LoadingChip url={`/${PATHS[lookup_key]}/${_uuid}`} icon={<ICON/>} {...chipProps}/>}
        error={error? error : (queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS[lookup_key]}/${_uuid}`}
            detail={queries[0].error?.response?.data?.toString()}
            key={_uuid}
            icon={<ICON />}
            variant="outlined"
            {...chipProps as ChipProps as any}
        />
        }
        success={success || <Chip
            key={_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICON />}
            variant="outlined"
            label={
                query.data?.data?
                    Object.keys(GET_REPRESENTATIONS).includes(lookup_key)?
                        GET_REPRESENTATIONS[lookup_key as keyof typeof GET_REPRESENTATIONS](query.data?.data) :
                        `${DISPLAY_NAMES[lookup_key]} ${_uuid}` :
                    ""
            }
            clickable={true}
            component={Link}
            to={`${PATHS[lookup_key]}/${_uuid}`}
            {...chipProps as ChipProps as any}
        />}
    />

}