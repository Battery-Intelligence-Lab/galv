// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {ReactNode} from "react";
import useStyles from "../styles/UseStyles";
import {useQuery, useQueryClient} from "@tanstack/react-query";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import axios, {AxiosError, AxiosResponse} from "axios";
import Stack from "@mui/material/Stack";
import clsx from "clsx";
import Grid from "@mui/material/Unstable_Grid2";
import CircularProgress from "@mui/material/CircularProgress";
import Skeleton from "@mui/material/Skeleton";
import ResourceCard, {BaseResource} from "./ResourceCard";
import ResourceCreator from "./ResourceCreator";
import {API_HANDLERS, API_SLUGS, DISPLAY_NAMES_PLURAL, LookupKey} from "../constants";
import ErrorBoundary from "./ErrorBoundary";
import {get_select_function} from "./ApiResourceContext";
import Button from "@mui/material/Button";
import {useCurrentUser} from "./CurrentUserContext";

type PaginatedAPIResponse<T = any> = {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}

export function ResourceList<T extends BaseResource>({lookup_key}: {lookup_key: LookupKey}) {
    const { classes } = useStyles();

    // API handler
    const api_handler = new API_HANDLERS[lookup_key]()
    const get = api_handler[
        `${API_SLUGS[lookup_key]}List` as keyof typeof api_handler
        ] as () => Promise<AxiosResponse<PaginatedAPIResponse<T>>>
    // Queries
    const queryClient = useQueryClient()
    const query = useQuery<AxiosResponse<PaginatedAPIResponse<T>>, AxiosError>({
        queryKey: [lookup_key, 'list'],
        queryFn: () => get.bind(api_handler)().then(r => {
            try {
                // Update the cache for each resource
                r.data.results.forEach((resource: T) => {
                    queryClient.setQueryData(
                        [lookup_key, resource.uuid ?? resource.id ?? "no id in List response"],
                        get_select_function(lookup_key)({
                            ...r,
                            data: resource
                        })
                    )
                })
            } catch (e) {
                console.error("Error updating cache from list data.", e)
            }
            return r
        })
    })

    const {setLoginFormOpen} = useCurrentUser()

    let content: ReactNode

    if (query.isInitialLoading) {
        content = Array(5).fill(0).map((_, i) => <Skeleton key={i} variant="rounded" height="6em"/>)
    } else if (!query.data || query.data.data.results.length === 0) {
        if (!axios.defaults.headers.common['Authorization'])
            content = <p><Button onClick={() => setLoginFormOpen(true)}>Log in</Button> to see {DISPLAY_NAMES_PLURAL[lookup_key]}</p>
        else
            content = <p>No {DISPLAY_NAMES_PLURAL[lookup_key].toLowerCase()} on the server are visible for this account.</p>
    } else {
        content = query.data.data.results.map(
            (resource: T, i) => <ResourceCard
                key={`resource_${i}`}
                resource_id={resource.uuid as string ?? resource.id as number}
                lookup_key={lookup_key}
            />
        )
    }

    return (
        <Container maxWidth="lg">
            <Grid container justifyContent="space-between" key="header">
                <Typography
                    component="h1"
                    variant="h3"
                    className={clsx(classes.pageTitle, classes.text)}
                >
                    {DISPLAY_NAMES_PLURAL[lookup_key]}
                    {query.isLoading && <CircularProgress sx={{color: (t) => t.palette.text.disabled, marginLeft: "1em"}} />}
                </Typography>
            </Grid>
            <Stack spacing={2} key="body">
                {content}
                <ResourceCreator key={'creator'} lookup_key={lookup_key} />
            </Stack>
        </Container>
    );
}

export default function WrappedResourceList(props: {lookup_key: LookupKey}) {
    return <ErrorBoundary
        fallback={<p>{props.lookup_key}: Could not load {DISPLAY_NAMES_PLURAL[props.lookup_key]}</p>}
        key={props.lookup_key}
    >
        <ResourceList {...props} />
    </ErrorBoundary>
}