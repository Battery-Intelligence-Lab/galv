// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { render, screen } from '@testing-library/react';
import HarvesterEnv from '../HarvesterEnv';

it('has appropriate columns', () => {
    const harvester = {
        name: 'test-harvester',
        sleep_time: 10,
        environment_variables: {
            TMP_VAR: 'temporary value'
        },
        url: "http://localhost:5000/harvesters/1/",
        id: 1,
        last_check_in: null,
        user_sets: []
    }
    const {container} = render(
        <HarvesterEnv harvester={harvester} refreshCallback={()=>{}} />
    );
    expect(screen.getByText(/Variable/)).toBeInTheDocument();
    expect(screen.getByText(/Value/)).toBeInTheDocument();
    expect(screen.getByText(/Actions/)).toBeInTheDocument();

    expect(screen.getByText(`${harvester.name} - environment variables`)).toBeInTheDocument();
    expect(screen.getByText(`${Object.keys(harvester.environment_variables)[0]}`)).toBeInTheDocument();
    expect(screen.getByDisplayValue(`${harvester.environment_variables.TMP_VAR}`)).toBeInTheDocument();

    expect(screen.getByPlaceholderText(/NEW_VARIABLE/)).toBeInTheDocument();
    expect(screen.getAllByPlaceholderText(/VALUE/)).toHaveLength(2);
});