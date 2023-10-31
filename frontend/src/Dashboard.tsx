// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState} from "react";
import useStyles from "./UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CellModelsApi} from "./api_codegen";
import Paper from "@mui/material/Paper";
import Container from "@mui/material/Container";
export default function Dashboard() {
  const { classes } = useStyles();

  // API handler
  const api_handler = new CellModelsApi()
  // Queries
  const query = useQuery({
    queryKey: ['cell_models'],
    queryFn: () => api_handler.cellModelsList()
  })

  return (
    <Container maxWidth="lg" className={classes.container}>
      <Paper className={classes.paper}>
        <h1>Dashboard</h1>
        <p>Cell models</p>
        <ul>
            {query.data?.data?.results?.map((cellModel: string) => (
                <li key={cellModel}>
                    {cellModel}
                </li>
            ))}
        </ul>
      </Paper>
    </Container>
  );
}