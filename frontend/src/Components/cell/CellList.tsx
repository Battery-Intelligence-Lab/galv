// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState} from "react";
import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CellFamiliesApi, CellFamily, PaginatedCellFamilyList} from "../../api_codegen";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import {AxiosError, AxiosResponse} from "axios";
import Stack from "@mui/material/Stack";
import clsx from "clsx";
import Grid from "@mui/material/Unstable_Grid2";
import CircularProgress from "@mui/material/CircularProgress";
import Skeleton from "@mui/material/Skeleton";
import FilterBar from "../filtering/FilterBar";
import TextFilter from "../filtering/TextFilter";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import ErrorPage from "../error/ErrorPage";
import CellFamilyCard from "./CellFamilyCard";


export default function CellList() {
    const { classes } = useStyles();
    const [filteredData, setFilteredData] = useState<CellFamily[]>([])

    // API handler
    const api_handler = new CellFamiliesApi()
    // Queries
    const query = useQuery<AxiosResponse<PaginatedCellFamilyList>, AxiosError>({
        queryKey: ['cell_families_list'],
        queryFn: () => api_handler.cellFamiliesList()
    })

    const loadingContent = <Stack spacing={2}>
        {
            query.isInitialLoading && [1, 2, 3, 4, 5].map((i) =>
                <Skeleton key={i} variant="rounded" height="6em"/>
            )
        }
    </Stack>

    const body =
        <Stack spacing={2}>
            {filteredData.map((cell_family: CellFamily) => <CellFamilyCard key={cell_family.uuid} uuid={cell_family.uuid} />)}
        </Stack>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorPage
        status={queries.find(q => q.isError)?.error?.response?.status}
        />

    return (
        <Container maxWidth="lg" className={classes.container}>
            <Grid container justifyContent="space-between">
                <Typography
                    component="h1"
                    variant="h3"
                    className={clsx(classes.page_title, classes.text)}
                >
                    Cells
                    {query.isLoading && <CircularProgress sx={{color: (t) => t.palette.text.disabled, marginLeft: "1em"}} />}
                </Typography>
                <FilterBar
                    data={query.data?.data?.results}
                    filters={{uuid: {target_key: 'uuid', label: 'Family UUID matches', widget: TextFilter}}}
                    setFilteredData={setFilteredData}
                />
            </Grid>
            <QueryWrapper
                queries={[query]}
                loading={loadingContent}
                error={getErrorBody}
                success={body}
            />
        </Container>
    );
}
