// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_users from './fixtures/users.json';
const mock_user = mock_users[0]
const UserProfile = jest.requireActual('../UserProfile').default;

// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked_update = jest.spyOn(Connection, 'update_user')
const mocked_login = jest.spyOn(Connection, 'login')

describe('Equipment', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(async () => {
        mocked_login.mockImplementation(() => Connection.user = mock_user)
        await Connection.login()
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked_update.mockResolvedValue(mock_user);
        let container
        await act(async () => container = render(<UserProfile />).container);
    })

    it('has appropriate values', async () => {
        expect(await screen.findByText(`${mock_user.username} profile`)).toBeInTheDocument();
        expect(await screen.getAllByRole('textbox').find(e => /email/i.test(e.name))).toBeInTheDocument();
        expect(await screen.findByDisplayValue(mock_user.email)).toBeInTheDocument();
        expect(await screen.getAllByLabelText(/password/i).find(e => /password/i.test(e.name))).toBeInTheDocument();
        expect(await screen.getAllByLabelText(/password/i).find(e => /currentPassword/i.test(e.name))).toBeInTheDocument();
    });

    it('sends an API call when updated', async () => {
        await user.clear(screen.getAllByRole('textbox').find(e => /email/i.test(e.name)))
        await user.type(screen.getAllByRole('textbox').find(e => /email/i.test(e.name)), 'x')
        await user.click(screen.getByRole('submit'));

        expect(mocked_update).toHaveBeenCalledWith('x', '', '')
    }, 10000)
});
