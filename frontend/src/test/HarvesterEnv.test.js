// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_harvesters from './fixtures/harvesters.json';
const HarvesterEnv = jest.requireActual('../HarvesterEnv').default;

var mock_harvester = mock_harvesters[1]
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
        expect(screen.getAllByRole('columnheader').find(e => /Variable/.test(e.textContent))).toBeInTheDocument();
        expect(screen.getAllByRole('columnheader').find(e => /Value/.test(e.textContent))).toBeInTheDocument();
        expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();

        expect(screen.getByText(`${mock_harvester.name} - environment variables`)).toBeInTheDocument();
        expect(screen.getByText(`${Object.keys(mock_harvester.environment_variables)[0]}`)).toBeInTheDocument();
        expect(screen.getByDisplayValue(`${mock_harvester.environment_variables.TMP_VAR}`)).toBeInTheDocument();

        expect(screen.getByPlaceholderText(/NEW_VARIABLE/)).toBeInTheDocument();
        expect(screen.getAllByPlaceholderText(/VALUE/)).toHaveLength(2);
    });

    it('sends update API call for editing variables', async () => {
        const key = Object.keys(mock_harvester.environment_variables)[0]
        const new_value = 'new value'
        await user.type(
            screen.getByDisplayValue(mock_harvester.environment_variables[key]),
            `{Backspace>20}${new_value}`
        )
        await user.click(screen.getAllByTestId('SaveIcon')[0])

        expect (mocked).toHaveBeenCalledWith(
            mock_harvester.url,
            {
                body: JSON.stringify({
                    environment_variables: {
                        [key]: new_value,
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
            mock_harvester.url,
            {
                body: JSON.stringify({
                    environment_variables: {
                        ...mock_harvester.environment_variables,
                        TEST_OUTCOME: 'success?'
                    }
                }),
                method: 'PATCH'
            }
        )
    });
})
