import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props} from "./misc";
import LoadingChip from "../utils/LoadingChip";
import QueryWrapper, {QueryWrapperProps} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {
    API_HANDLERS,
    PATHS, ICONS, API_SLUGS, FAMILY_LOOKUP_KEYS, LookupKey
} from "../../constants";
import {Family} from "./ResourceCard";
import ErrorBoundary from "./ErrorBoundary";
import Representation from "./Representation";

type ResourceFamilyChipProps = {
    resource_id: string|number
    lookup_key: LookupKey
    short_name?: boolean
}

export default function ResourceChip<T extends Family>(
    {resource_id, lookup_key, loading, error, success, short_name, ...chipProps}:
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
                label={<Representation
                    resource_id={resource_id}
                    lookup_key={lookup_key}
                    prefix={(!short_name && query.data?.data.family) ?
                        <Representation
                            resource_id={id_from_ref_props<string>(query.data?.data.family)}
                            lookup_key={FAMILY_LOOKUP_KEYS[lookup_key as keyof typeof FAMILY_LOOKUP_KEYS]}
                            suffix=" "
                        /> : undefined
                    }
                />}
                clickable={true}
                component={Link}
                to={`${PATHS[lookup_key]}/${resource_id}`}
                {...chipProps as ChipProps as any}
            />}
        />
    </ErrorBoundary>
}