// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_files from './fixtures/files.json';
import mock_monitored_paths from './fixtures/monitored_paths.json';
const mock_monitored_path = mock_monitored_paths[0];
const Files = jest.requireActual('../Files').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Files has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Files path={mock_monitored_path} />));
    expect(screen.getAllByRole('columnheader').find(e => e.textContent === mock_monitored_path.path)).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Size/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Time/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /State/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Datasets/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Re-import/.test(e.textContent))).toBeInTheDocument();
})

describe('Files', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_files.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_files.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Files path={mock_monitored_path} />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            `files/?monitored_path__id=${mock_monitored_path.id}`,
            {},
            false
        )

        expect(await screen.findByText(mock_files[0].path)).toBeInTheDocument();
    });

    it('sends an API call when reimported', async () => {
        await user.click(screen.getAllByRole('button', {name: /Re-import/i})[0]);

        expect(mocked_fetch).toHaveBeenCalledWith(`${mock_files[0].url}reimport/`)
    })
});
