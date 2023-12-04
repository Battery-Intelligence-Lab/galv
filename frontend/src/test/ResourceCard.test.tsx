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

jest.mock('../Components/Representation')
jest.mock('../Components/ResourceChip')
jest.mock('../Components/CardActionBar')
jest.mock('../Components/prettify/PrettyObject')

// Mock jest and set the type
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const ResourceCard = jest.requireActual('../Components/ResourceCard').default;

const data = {
    uuid: "0001-0001-0001-0001",
    identifier: 'Test Cell 1',
    family: "http://example.com/cell_families/1000-1000-1000-1000",
    team: "http://example.com/teams/1",
    customProperty: {
        exists: true,
        value: "custom",
        nested: {
            exists: true,
            value: ["yes", "nested"],
        }
    }
}

const family_data = {
    uuid: "1000-1000-1000-1000",
    identifier: 'Test Cell Family 1',
    team: "http://example.com/teams/1"
}

it('renders', async () => {
    mockedAxios.request.mockResolvedValueOnce({data}).mockResolvedValueOnce({data: family_data});

    const queryClient = new QueryClient();

    render(
        <MemoryRouter initialEntries={["/"]}>
            <FilterContextProvider>
                <QueryClientProvider client={queryClient}>
                    <ResourceCard lookup_key={LOOKUP_KEYS.CELL} resource_id="0001-0001-0001-0001" expanded />
                </QueryClientProvider>
            </FilterContextProvider>
        </MemoryRouter>
    )
    await screen.findAllByText(/PrettyObject/)
    expect(screen.getAllByText(/PrettyObject/)).toHaveLength(3)
})
