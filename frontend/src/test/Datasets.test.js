// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_datasets from './fixtures/datasets.json';
const Datasets = jest.requireActual('../Datasets').default;

jest.mock('../DatasetChart')

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Datasets has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Datasets />));
    expect(screen.getAllByRole('columnheader').find(e => /Date/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Properties/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Equipment/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();
})

describe('Datasets', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_datasets.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_datasets.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Datasets />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'datasets/',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_datasets[0].name)).toBeInTheDocument();
    });

    it('spawns child components when the button is clicked', async () => {
        await act(async () => await user.click(screen.getAllByTestId(/SearchIcon/)[0]));
        expect(await screen.findByText(/MockDatasetChart/)).toBeInTheDocument();
    });

    it('sends an update API call when saved', async () => {
        const name = await screen.findByDisplayValue(mock_datasets[0].name)
        await user.clear(name)
        await user.type(name, 'T')
        await user.click(await screen.getAllByRole('button').find(e => /^Save$/.test(e.textContent)))
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_datasets[0].url,
            {
                body: JSON.stringify({
                    name: "T",
                    type: mock_datasets[0].type,
                    cell: mock_datasets[0].cell,
                    equipment: mock_datasets[0].equipment
                }),
                method: 'PATCH'
            }
        )
    });
});
