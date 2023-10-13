// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState} from "react";
import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CyclerTest, CyclerTestsApi} from "../../api_codegen";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import {Link} from "react-router-dom";
import axios from "axios";
import Stack from "@mui/material/Stack";
import clsx from "clsx";
import Grid from "@mui/material/Unstable_Grid2";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Skeleton from "@mui/material/Skeleton";
import FilterBar from "../filtering/FilterBar";
import TextFilter from "../filtering/TextFilter";
import CyclerTestCard from "./CyclerTestCard";


export default function CyclerTestList() {
    const { classes } = useStyles();
    const [filteredData, setFilteredData] = useState<CyclerTest[]>([])

    // API handler
    const api_handler = new CyclerTestsApi()
    // Queries
    const query = useQuery({
        queryKey: ['cycler_tests_list'],
        queryFn: () => api_handler.cyclerTestsList()
    })

    return (
        <Container maxWidth="lg" className={classes.container}>
            <Grid container justifyContent="space-between">
                <Typography
                    component="h1"
                    variant="h3"
                    className={clsx(classes.page_title, classes.text)}
                >
                    Cycler Tests
                    {query.isLoading && <CircularProgress sx={{color: (t) => t.palette.text.disabled, marginLeft: "1em"}} />}
                </Typography>
                <FilterBar
                    data={query.data?.data?.results}
                    filters={{uuid: {target_key: 'uuid', label: 'UUID matches', widget: TextFilter}}}
                    setFilteredData={setFilteredData}
                />
            </Grid>
            <Stack spacing={2}>
                {
                    query.isInitialLoading && [1, 2, 3, 4, 5].map((i) =>
                        <Skeleton key={i} variant="rounded" height="6em"/>
                    )
                }
                { query.data?.data?.results && query.data.data.results.length === 0 ?
                    !axios.defaults.headers.common['Authorization']?
                        <p><Link to="/login">Log in</Link> to see Cycler Tests</p> :
                        <p>No Cycler Tests found</p> :
                    filteredData.map(
                        (cycler_test: CyclerTest) => <CyclerTestCard uuid={cycler_test.uuid} />
                    )
                }
            </Stack>
        </Container>
    );
}
