// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.


globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import ActivateUsers from "../ActivateUsers";
import mock_users from './fixtures/inactive_users.json';

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')

it('ActivateUsers has appropriate columns', async () => {
    mocked_fetchMany.mockResolvedValue([]);
    await act(async () => render(<ActivateUsers />));
    expect(screen.getAllByRole('columnheader').find(e => /Username/.test(e.textContent))).toBeInTheDocument();
    expect(screen.getAllByRole('columnheader').find(e => /Activate/.test(e.textContent))).toBeInTheDocument();
})

describe('ActivateUsers', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_fetchMany.mockResolvedValue(mock_users.map(u => ({content: u})));
        mocked_fetch.mockResolvedValue(null)
        let container
        await act(async () => container = render(<ActivateUsers />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith(
            `inactive_users/`,
            {},
            false
        )

        expect(screen.getAllByRole('cell').find(e => e.textContent === mock_users[0].username)).toBeInTheDocument();
    });

    it('sends an API call when user is activated', async () => {
        await user.click(screen.getAllByRole('button', {label: 'activate'})[0]);
        expect(mocked_fetch).toHaveBeenCalledWith(`${mock_users[0].url}vouch_for/`)
        expect(mocked_fetchMany).toHaveBeenCalledTimes(2)
    });
});
