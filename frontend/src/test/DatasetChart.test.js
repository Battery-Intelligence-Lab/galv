// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import React from 'react';
import {render, screen, waitFor} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Connection from "../APIConnection";
import mock_datasets from './fixtures/datasets.json';
import mock_columns from './fixtures/columns.json';
import mock_data from './fixtures/data.json';
const DatasetChart = jest.requireActual('../DatasetChart').default;

var mock_dataset = mock_datasets[1]
// Mock the APIConnection.fetch function from the APIConnection module
// This is because we don't want to actually make API calls in our tests
// We just want to check that the correct calls are made
const mocked = jest.spyOn(Connection, 'fetch')

describe.skip('DatasetChart', () => {
    let container;
    const user = userEvent.setup();

    beforeEach(() => {
        // The mock implementation needs to occur here; if it's done outside it doesn't work!
        mocked.mockImplementation((url) => {
            if (/data_listformat\/$/.test(url))
                return new Promise((resolve) => ({content: mock_data}))
            return new Promise((resolve) => ({content: mock_columns.find(c => c.url === url)}))
        });
        container = render(
            <DatasetChart dataset={mock_dataset} />
        ).container;
    })

    it('has appropriate columns', async () => {
        await new Promise((resolve) => setTimeout(resolve, 3000))
        screen.debug(undefined, 200000000)
    });
})