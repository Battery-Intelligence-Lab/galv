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
import ErrorCard from "../error/ErrorCard";
import CardHeader from "@mui/material/CardHeader";
import Avatar from "@mui/material/Avatar";
import ErrorBoundary from "./ErrorBoundary";
import Representation from "./Representation";

type ResourceFamilyChipProps = {
    resource_id: string|number
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof DISPLAY_NAMES &
        keyof typeof API_HANDLERS &
        string
}

export default function ResourceChip<T extends Family>(
    {resource_id, lookup_key, loading, error, success, ...chipProps}:
        ResourceFamilyChipProps & Partial<QueryWrapperProps> & ChipProps & {component?: React.ElementType}
) {
    // console.log(`ResourceChip`, {uuid, lookup_key, loading, error, success, chipProps})
    const { classes } = useStyles();

    const ICON = ICONS[lookup_key]

    const api_handler = new API_HANDLERS[lookup_key]()
    const api_get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, resource_id],
        queryFn: () => api_get.bind(api_handler)(String(resource_id))
    })

    return <ErrorBoundary
        fallback={(error: Error) => <ErrorChip
            target={`${lookup_key} ${resource_id}`}
            detail={error.message}
            key={resource_id}
            icon={<ICON />}
            variant="outlined"
        />}
    >
        <QueryWrapper
            queries={[query]}
            loading={loading || <LoadingChip url={`/${PATHS[lookup_key]}/${resource_id}`} icon={<ICON/>} {...chipProps}/>}
            error={error? error : (queries) => <ErrorChip
                status={queries[0].error?.response?.status}
                target={`${PATHS[lookup_key]}/${resource_id}`}
                detail={queries[0].error?.response?.data?.toString()}
                key={resource_id}
                icon={<ICON />}
                variant="outlined"
                {...chipProps as ChipProps as any}
            />
            }
            success={success || <Chip
                key={resource_id}
                className={clsx(classes.item_chip)}
                icon={<ICON />}
                variant="outlined"
                label={<Representation resource_id={resource_id} lookup_key={lookup_key}/>}
                clickable={true}
                component={Link}
                to={`${PATHS[lookup_key]}/${resource_id}`}
                {...chipProps as ChipProps as any}
            />}
        />
    </ErrorBoundary>
}