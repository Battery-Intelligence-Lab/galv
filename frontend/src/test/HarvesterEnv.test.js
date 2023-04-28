// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import HarvesterEnv from '../HarvesterEnv';

var mock_harvester = {
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
// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked = jest.spyOn(Connection, 'fetch')

describe('HarvesterEnv', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(() => {
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked.mockResolvedValue({content: mock_harvester});
        container = render(
            <HarvesterEnv harvester={mock_harvester} refreshCallback={()=>{}} />
        ).container;
    })

    it('has appropriate columns', () => {
        expect(screen.getByText(/Variable/)).toBeInTheDocument();
        expect(screen.getByText(/Value/)).toBeInTheDocument();
        expect(screen.getByText(/Actions/)).toBeInTheDocument();

        expect(screen.getByText(`${mock_harvester.name} - environment variables`)).toBeInTheDocument();
        expect(screen.getByText(`${Object.keys(mock_harvester.environment_variables)[0]}`)).toBeInTheDocument();
        expect(screen.getByDisplayValue(`${mock_harvester.environment_variables.TMP_VAR}`)).toBeInTheDocument();

        expect(screen.getByPlaceholderText(/NEW_VARIABLE/)).toBeInTheDocument();
        expect(screen.getAllByPlaceholderText(/VALUE/)).toHaveLength(2);
    });

    it('sends update API call for editing variables', async () => {
        // TODO currently doesn't work because of the auto-updating from HarvesterEnv
        const new_value = 'new value'
        await user.type(
            screen.getByDisplayValue(mock_harvester.environment_variables.TMP_VAR),
            `{Backspace>20}${new_value}`
        )
        await user.click(screen.getAllByTestId('SaveIcon')[0])

        expect (mocked).toHaveBeenCalledWith(
            'http://localhost:5000/harvesters/1/',
            {
                body: JSON.stringify({
                    environment_variables: {
                        TMP_VAR: new_value,
                    }
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends update API call for new var', async () => {
        // TODO currently doesn't work because of the auto-updating from HarvesterEnv
        await user.type(screen.getByPlaceholderText(/NEW_VARIABLE/), 'TEST_OUTCOME')
        await user.type(screen.getAllByPlaceholderText(/VALUE/)[1], 'success?')
        await user.click(screen.getByTestId('AddIcon'))

        expect (mocked).toHaveBeenCalledWith(
            'http://localhost:5000/harvesters/1/',
            {
                body: JSON.stringify({
                    environment_variables: {
                        TMP_VAR: 'temporary value',
                        TEST_OUTCOME: 'success?'
                    }
                }),
                method: 'PATCH'
            }
        )
    });
})
