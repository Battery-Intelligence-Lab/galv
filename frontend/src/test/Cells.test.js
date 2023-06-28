// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_cell_families from './fixtures/cell_families.json';
const Cells = jest.requireActual('../Cells').default;

jest.mock('../CellList')

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Cells has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Cells />));
    expect(screen.getAllByRole('columnheader').find(e => /Source/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Type/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Chemistry/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Statistics/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();
})

describe('Cells', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_cell_families.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_cell_families.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Cells />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'cell_families/',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_cell_families[0].name)).toBeInTheDocument();
    });

    it('spawns child components when the button is clicked', async () => {
        await act(async () => await user.click(screen.getAllByTestId(/SearchIcon/)[0]));
        expect(await screen.findByText(/MockCellList/)).toBeInTheDocument();
    });

    it('sends an API call when created', async () => {
        const n = mock_cell_families.length
        await user.type(screen.getAllByRole('textbox', {name: /Name/i})[n], 'x')
        await user.click(screen.getAllByRole('button', {name: /Save/i})[n]);

        expect(mocked_fetch).toHaveBeenCalledWith(
            'cell_families/',
            {
                body: JSON.stringify({
                    name: 'x',
                    form_factor: '',
                    link_to_datasheet: '',
                    manufacturer: '',
                    anode_chemistry: '',
                    cathode_chemistry: '',
                    nominal_capacity: 0,
                    nominal_cell_weight: 0,
                }),
                method: 'POST'
            }
        )
    }, 10000)

    it('sends an update API call when saved', async () => {
        const name = await screen.findByDisplayValue(mock_cell_families[0].name)
        await user.clear(name)
        await user.type(name, 'T')
        await user.click(await screen.getAllByRole('button').find(e => /^Save$/.test(e.textContent)))
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_cell_families[0].url,
            {
                body: JSON.stringify({
                    name: "T",
                    form_factor: mock_cell_families[0].form_factor,
                    link_to_datasheet: mock_cell_families[0].link_to_datasheet,
                    manufacturer: mock_cell_families[0].manufacturer,
                    anode_chemistry: mock_cell_families[0].anode_chemistry,
                    cathode_chemistry: mock_cell_families[0].cathode_chemistry,
                    nominal_capacity: mock_cell_families[0].nominal_capacity,
                    nominal_cell_weight: mock_cell_families[0].nominal_cell_weight,
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByRole('button').find(e => /^Delete$/.test(e.textContent))))
        expect(window.confirm).toHaveBeenCalledWith(`Delete cell family ${mock_cell_families[0].name}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_cell_families[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
