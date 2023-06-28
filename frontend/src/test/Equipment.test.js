// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_equipment from './fixtures/equipment.json';
const Equipment = jest.requireActual('../Equipment').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Equipment has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Equipment />));
    expect(screen.getAllByRole('columnheader').find(e => /Name/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Type/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Save/.test(e.textContent))).toBeInTheDocument();
})

describe('Equipment', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_equipment.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_equipment.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Equipment />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'equipment/',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_equipment[0].name)).toBeInTheDocument();
    });

    it('sends an API call when created', async () => {
        const n = mock_equipment.length
        await user.type(screen.getAllByRole('textbox').filter(e => /name/i.test(e.name))[n], 'x')
        await user.click(screen.getAllByRole('button', {name: /Save/i})[n]);

        expect(mocked_fetch).toHaveBeenCalledWith(
            'equipment/',
            {
                body: JSON.stringify({
                    name: 'x',
                    type: "",
                }),
                method: 'POST'
            }
        )
    }, 10000)

    it('sends an update API call when saved', async () => {
        const name = await screen.findByDisplayValue(mock_equipment[0].name)
        await user.clear(name)
        await user.type(name, 'T')
        await user.click(await screen.getAllByRole('button').find(e => /^Save$/.test(e.textContent)))
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_equipment[0].url,
            {
                body: JSON.stringify({
                    name: "T",
                    type: mock_equipment[0].type,
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByRole('button').find(e => /^Delete$/.test(e.textContent))))
        expect(window.confirm).toHaveBeenCalledWith(`Delete equipment ${mock_equipment[0].name}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_equipment[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
