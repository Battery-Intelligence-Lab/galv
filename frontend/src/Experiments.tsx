// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState} from "react";
import useStyles from "./UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CellModelsApi, ExperimentsApi} from "./api_codegen";
import Paper from "@mui/material/Paper";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import {Link} from "react-router-dom";
import Login from "./Login";
import axios from "axios";
export default function Experiments() {
    const { classes } = useStyles();

    // API handler
    const api_handler = new ExperimentsApi()
    // Queries
    const query = useQuery({
        queryKey: ['experiments_list'],
        queryFn: () => api_handler.experimentsList()
    })

    return (
        <Container maxWidth="lg" className={classes.container}>
            <Typography
                component="h1"
                variant="h3"
                className={[classes.page_title, classes.text].join(" ")}
            >Experiments {query.isLoading && <span>...</span>}</Typography>
            {
                query.isInitialLoading && <p>Loading...</p>
            }
            { query.data?.data?.results && query.data.data.results.length === 0 ?
                !axios.defaults.headers.common['Authorization']?
                    <p><Link to="/login">Log in</Link> to see experiments</p> :
                    <p>No experiments found</p> :
                <ul>
                    {query.data?.data?.results?.map((experiment: any) => (
                        <li key={experiment.uuid}>
                            {experiment}
                        </li>
                    ))}
                </ul>
            }
        </Container>
    );
}
