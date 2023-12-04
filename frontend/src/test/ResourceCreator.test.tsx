// // SPDX-License-Identifier: BSD-2-Clause
// // Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// // of Oxford, and the 'Galv' Developers. All rights reserved.

// globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import {LOOKUP_KEYS} from "../constants";
import React from 'react';
import { render, screen } from '@testing-library/react';
import axios from 'axios';
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {FilterContextProvider} from "../Components/filtering/FilterContext";
import {MemoryRouter} from "react-router-dom";
import userEvent from "@testing-library/user-event";

jest.mock('../Components/CardActionBar')
jest.mock('../Components/prettify/PrettyObject')

// Mock jest and set the type
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const ResourceCreator = jest.requireActual('../Components/ResourceCreator').default;

const family_data = {
    uuid: "1000-1000-1000-1000",
    identifier: 'Test Cell Family 1',
    team: "http://example.com/teams/1"
}
const results = [family_data]

it('renders', async () => {
    mockedAxios.request.mockResolvedValue({data: {results}});

    const queryClient = new QueryClient();

    render(
        <MemoryRouter initialEntries={["/"]}>
            <FilterContextProvider>
                <QueryClientProvider client={queryClient}>
                    <ResourceCreator lookup_key={LOOKUP_KEYS.CELL} />
                </QueryClientProvider>
            </FilterContextProvider>
        </MemoryRouter>
    )
    await userEvent.click(screen.getByRole('button'))
    await screen.findByText(/DummyPrettyObject/)
})
