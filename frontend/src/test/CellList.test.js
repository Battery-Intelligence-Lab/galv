// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_cells from './fixtures/cells.json';
import mock_cell_families from './fixtures/cell_families.json';

const mock_cell_family = mock_cell_families.find(f => f.url === mock_cells[0].family)
const CellList = jest.requireActual('../CellList').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('CellList has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<CellList family={mock_cell_family}/>));
    expect(screen.getAllByRole('columnheader').find(element => /UID/.test(element.textContent))).toBeInTheDocument()
    expect(screen.getAllByRole('columnheader').find(element => /Display Name/.test(element.textContent))).toBeInTheDocument()
    expect(screen.getAllByRole('columnheader').find(element => /Linked Datasets/.test(element.textContent))).toBeInTheDocument()
    expect(screen.getAllByRole('columnheader').find(element => /Actions/.test(element.textContent))).toBeInTheDocument()
})

describe('CellList', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_cells.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_cells.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<CellList family={mock_cell_family}/>).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'cells/',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_cells[0].uid)).toBeInTheDocument();
    });

    it('sends an API call when created', async () => {
        const n = mock_cells.length
        await act(async () => {
            await user.type(screen.getAllByRole('textbox', {name: /UID/i})[n], 'abc-123')
            await user.click(screen.getAllByRole('button', {name: /Save/i})[n]);
        })
        expect(mocked_fetch).toHaveBeenCalledWith(
            'cells/',
            {
                body: JSON.stringify({
                    uid: 'abc-123',
                    family: mock_cell_family.url
                }),
                method: 'POST'
            }
        )
    })

    it('sends an update API call when saved', async () => {
        await act(async () => {
            const name = await screen.findByDisplayValue(mock_cells[0].uid)
            await user.type(name, '{Backspace>20}xyz-098')
            await user.click(await screen.getAllByLabelText(/^Save$/)[0])
        });
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_cells[0].url,
            {
                body: JSON.stringify({
                    uid: 'xyz-098',
                    display_name: mock_cells[0].display_name,
                    family: mock_cell_family.url
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByTestId(/DeleteIcon/)[0]));
        expect(window.confirm).toHaveBeenCalledWith(`Delete cell ${mock_cells[0].display_name}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_cells[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
