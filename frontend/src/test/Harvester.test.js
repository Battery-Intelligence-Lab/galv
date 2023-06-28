// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_harvester from './fixtures/harvesters.json';
const Harvesters = jest.requireActual('../Harvesters').default;

jest.mock('../HarvesterDetail')
jest.mock('../HarvesterEnv')

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Harvester has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Harvesters />));
    expect(screen.getAllByRole('columnheader').find(e => /ID/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Name/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Last Check In/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Sleep Time \(s\)/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();
})

describe('Harvester', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_harvester.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_harvester.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Harvesters />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'harvesters/mine',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_harvester[0].name)).toBeInTheDocument();
    });

    it('spawns child components when the button is clicked', async () => {
        await act(async () => await user.click(screen.getAllByTestId(/SearchIcon/)[0]));
        expect(await screen.findByText(/MockHarvesterDetail/)).toBeInTheDocument();
        expect(await screen.findByText(/MockHarvesterEnv/)).toBeInTheDocument();
    });

    it('sends an update API call when saved', async () => {
        await act(async () => {
            const name = await screen.findByDisplayValue(mock_harvester[0].name)
            await user.type(name, '{Backspace>20}TEST_NAME')
            await user.click(await screen.getAllByLabelText(/^Save$/)[0])
        });
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_harvester[0].url,
            {
                body: JSON.stringify({
                    name: 'TEST_NAME',
                    sleep_time: mock_harvester[0].sleep_time,
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByTestId(/DeleteIcon/)[0]));
        expect(window.confirm).toHaveBeenCalledWith(`Delete ${mock_harvester[0].name}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_harvester[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
