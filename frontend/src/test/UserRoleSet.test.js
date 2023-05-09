// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_harvesters from './fixtures/harvesters.json';
import mock_users from './fixtures/users.json';
const mock_user_sets = mock_harvesters[0].user_sets
const UserRoleSet = jest.requireActual('../UserRoleSet').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_fetch = jest.spyOn(Connection, 'fetch')
const mocked_fetchMany = jest.spyOn(Connection, 'fetchMany')
const mocked_login = jest.spyOn(Connection, 'login')

describe('UserRoleSet', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = {username: 'admin'})
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_fetchMany.mockResolvedValue(mock_users.map(h => ({content: h})));
        mocked_fetch.mockImplementation(request => new Promise(resolve => ({content: mock_user_sets.find(h => h.url === request)})));
        let container
        await act(async () => container = render(<UserRoleSet user_sets={mock_user_sets} last_updated={new Date()} set_last_updated={(d) => {}} />).container);
    })

    it('has appropriate values', async () => {
        expect(mocked_fetchMany).toHaveBeenCalledWith('users/')

        expect(await screen.findByText(mock_user_sets[0].name)).toBeInTheDocument();
    });
});
