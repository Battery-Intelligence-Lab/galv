// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ActionButtons from '../ActionButtons';

var mock_inspect = jest.fn()
var mock_save = jest.fn()
var mock_delete = jest.fn()

describe('ActionButtons', () => {
    const user = userEvent.setup();

    it('defaults to disabled buttons', async () => {
        await act(async () => render(<ActionButtons />));
        expect(screen.queryByLabelText(/^Inspect$/)).toBeNull();
        expect(screen.queryByLabelText(/^Save$/)).toBeNull();
        expect(screen.queryByLabelText(/^Delete$/)).toBeNull();
    });

    it('calls the inspect function when clicked', async () => {
        await act(async () => render(<ActionButtons onInspect={mock_inspect} />));
        await act(async () => await user.click(screen.getByLabelText(/^Inspect$/)));
        expect(mock_inspect).toHaveBeenCalled();
    });

    it('calls the save function when clicked', async () => {
        await act(async () => render(<ActionButtons onSave={mock_save} />));
        await act(async () => await user.click(screen.getByLabelText(/^Save$/)));
        expect(mock_save).toHaveBeenCalled();
    });

    it('calls the delete function when clicked', async () => {
        await act(async () => render(<ActionButtons onDelete={mock_delete} />));
        await act(async () => await user.click(screen.getByLabelText(/^Delete$/)));
        expect(mock_delete).toHaveBeenCalled();
    });
});
