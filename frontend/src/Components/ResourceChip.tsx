import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../styles/UseStyles";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React, {useContext} from "react";
import LoadingChip from "./LoadingChip";
import QueryWrapper, {QueryWrapperProps} from "./QueryWrapper";
import ErrorChip from "./error/ErrorChip";
import {PATHS, FAMILY_LOOKUP_KEYS, LookupKey} from "../constants";
import {Family} from "./ResourceCard";
import ErrorBoundary from "./ErrorBoundary";
import Representation from "./Representation";
import {FilterContext} from "./filtering/FilterContext";
import ApiResourceContextProvider, {useApiResource} from "./ApiResourceContext";
import LookupKeyIcon from "./LookupKeyIcon";

type ResourceFamilyChipProps = {
    resource_id: string|number
    lookup_key: LookupKey
    short_name?: boolean
} & Partial<QueryWrapperProps> & ChipProps & {component?: React.ElementType}

export function ResourceChip<T extends Family>(
    {resource_id, lookup_key, loading, error, success, short_name, ...chipProps}: ResourceFamilyChipProps
) {
    // console.log(`ResourceChip`, {uuid, lookup_key, loading, error, success, chipProps})
    const { classes } = useStyles();

    const {passesFilters} = useContext(FilterContext)
    const {apiResource, family, apiQuery} = useApiResource<T>()

    const passes = passesFilters({apiResource, family}, lookup_key)

    const icon = <LookupKeyIcon lookupKey={lookup_key}/>

    return <QueryWrapper
        queries={apiQuery? [apiQuery] : []}
        loading={loading || <LoadingChip url={`/${PATHS[lookup_key]}/${resource_id}`} icon={icon} {...chipProps}/>}
        error={error? error : (queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS[lookup_key]}/${resource_id}`}
            detail={queries[0].error?.response?.data?.toString()}
            key={resource_id}
            icon={icon}
            variant="outlined"
            {...chipProps as ChipProps as any}
        />
        }
        success={success || <Chip
            key={resource_id}
            className={clsx(classes.itemChip, {'filter_failed': !passes})}
            icon={icon}
            variant="outlined"
            label={<Representation
                resource_id={resource_id}
                lookup_key={lookup_key}
                prefix={(!short_name && family) ?
                    <Representation
                        resource_id={family.uuid as string}
                        lookup_key={FAMILY_LOOKUP_KEYS[lookup_key as keyof typeof FAMILY_LOOKUP_KEYS]}
                        suffix=" "
                    /> : undefined
                }
            />}
            clickable={true}
            component={passes? Link : undefined}
            to={passes? `${PATHS[lookup_key]}/${resource_id}` : undefined}
            {...chipProps as ChipProps as any}
        />}
    />
}

export default function WrappedResourceChip<T extends Family>(props: ResourceFamilyChipProps) {
    return <ErrorBoundary
        fallback={(error: Error) => <ErrorChip
            target={`${props.lookup_key} ${props.resource_id}`}
            detail={error.message}
            key={props.resource_id}
            icon={<LookupKeyIcon lookupKey={props.lookup_key}/>}
            variant="outlined"
        />}
    >
        <ApiResourceContextProvider lookup_key={props.lookup_key} resource_id={props.resource_id}>
            <ResourceChip<T> {...props}/>
        </ApiResourceContextProvider>
    </ErrorBoundary>
}