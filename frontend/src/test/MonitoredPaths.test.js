// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_paths from './fixtures/monitored_paths.json';
import mock_harvesters from './fixtures/harvesters.json';

jest.mock('../Files')
jest.mock('../UserRoleSet', () => ({user_in_sets: () => true}))

var mock_harvester = mock_harvesters[1]
const HarvesterDetail = jest.requireActual('../MonitoredPaths').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('MonitoredPaths has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<HarvesterDetail harvester={mock_harvester}/>));
    expect(screen.getAllByRole('columnheader').find(e => /Stable Time \(s\)/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Users/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();
})

describe('MonitoredPaths', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        mocked_fetchMany.mockResolvedValue(mock_paths.map(p => ({content: p})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_paths.find(p => p.url === request)})));
        let container
        await act(async () => container = render(<HarvesterDetail harvester={mock_harvester}/>).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            `monitored_paths/?harvester__id=${mock_harvester.id}`,
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_paths[0].path)).toBeInTheDocument();
    });

    it('spawns a child component when the button is clicked', async () => {
        await act(async () => await user.click(screen.getAllByTestId(/SearchIcon/)[0]));
        expect(screen.getByText(/Files/)).toBeInTheDocument();
    });

    it('sends an API call when a new Path is created', async () => {
        const new_path = '/some/where'
        const new_stable_time = 100
        await act(async () => {
            await user.type(screen.getAllByPlaceholderText(/path$/)[1], new_path);
            await user.type(screen.getAllByPlaceholderText(".*")[1], '{Backspace>5}^[[^T]');
            await user.type(screen.getAllByDisplayValue(
                mock_paths[0].stable_time)[1],
                `{Backspace>10}${new_stable_time.toString()}`
            );
            await user.click(screen.getAllByTestId(/AddIcon/)[0]);
        });
        expect(mocked_fetch).toHaveBeenCalledWith(
            'monitored_paths/',
            {
                body: JSON.stringify({
                    harvester: mock_harvester.url,
                    path: new_path,
                    regex: '^[^T]',
                    stable_time: new_stable_time.toString(),
                }),
                method: 'POST'
            }
        )
    });

    it('sends an update API call when saved', async () => {
        const new_path = '/some/where/else'
        await act(async () => {
            const name = await screen.findByDisplayValue(mock_paths[0].path)
            await user.type(name, `{Backspace>50}${new_path}`)
            await user.click(await screen.getAllByLabelText(/^Save$/)[0])
        });
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_paths[0].url,
            {
                body: JSON.stringify({
                    path: new_path,
                    stable_time: mock_paths[0].stable_time,
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByTestId(/DeleteIcon/)[0]));
        expect(window.confirm).toHaveBeenCalledWith(`Delete ${mock_paths[0].path}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_paths[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
