// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_tokens from './fixtures/tokens.json';
const Tokens = jest.requireActual('../Tokens').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

it('Tokens has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<Tokens />));
    expect(screen.getAllByRole('columnheader').find(e => /Name/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Created/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Expires/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Actions/.test(e.textContent))).toBeInTheDocument();
})

describe('Tokens', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_tokens.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_tokens.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<Tokens />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            'tokens/',
            {},
            false
        )

        expect(await screen.findByDisplayValue(mock_tokens[0].name)).toBeInTheDocument();
    });

    it('sends an API call when created', async () => {
        const n = mock_tokens.length
        await user.type(screen.getAllByRole('textbox').filter(e => /name/i.test(e.name))[n], 'x')
        await user.click(screen.getAllByRole('button', {name: /Save/i})[n]);

        expect(mocked_fetch).toHaveBeenCalledWith(
            'create_token/',
            {
                body: JSON.stringify({
                    name: 'x',
                    ttl: null,
                }),
                method: 'POST'
            }
        )
    }, 10000)

    it('sends an update API call when saved', async () => {
        const name = await screen.findByDisplayValue(mock_tokens[0].name)
        await user.clear(name)
        await user.type(name, 'T')
        await user.click(await screen.getAllByRole('button').find(e => /^Save$/.test(e.textContent)))
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_tokens[0].url,
            {
                body: JSON.stringify({
                    name: "T",
                    type: mock_tokens[0].type,
                }),
                method: 'PATCH'
            }
        )
    });

    it('sends an API call when deleted', async () => {
        window.confirm = jest.fn(() => true);
        await act(async () => await user.click(screen.getAllByRole('button').find(e => /^Delete$/.test(e.textContent))))
        expect(window.confirm).toHaveBeenCalledWith(`Delete token ${mock_tokens[0].name}?`);
        expect(mocked_fetch).toHaveBeenCalledWith(
            mock_tokens[0].url,
            {
                method: 'DELETE'
            }
        )
    });
});
