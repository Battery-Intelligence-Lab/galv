// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import {UserSet} from "../UserRoleSet";

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { render, screen } from '@testing-library/react';
import HarvesterEnv from '../HarvesterEnv';
import { createTheme, StyledEngineProvider } from '@mui/material/styles';
import { ThemeProvider } from "@mui/styles";

it('renders', () => {
    const harvester = {
        name: 'test-harvester',
        sleep_time: 10,
        environment_variables: [],
        url: "http://localhost:5000/harvesters/1/",
        id: 1,
        last_check_in: null,
        user_sets: []
    }
    const theme = createTheme();
    render(
        <ThemeProvider theme={theme}>
            <StyledEngineProvider injectFirst>
                <HarvesterEnv harvester={harvester} refreshCallback={()=>{}} />
            </StyledEngineProvider>
        </ThemeProvider>
    );
    expect(screen.getByText('Variable')).toBeInTheDocument();
});