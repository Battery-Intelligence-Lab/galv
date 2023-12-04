// // SPDX-License-Identifier: BSD-2-Clause
// // Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// // of Oxford, and the 'Galv' Developers. All rights reserved.

// globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import {LOOKUP_KEYS} from "../constants";
import React from 'react';
import { render, screen } from '@testing-library/react';
import axios from 'axios';
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";

jest.mock('../Components/ResourceCard')

// Mock jest and set the type
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const ResourceList = jest.requireActual('../Components/ResourceList').default;
const results = [
  {uuid: "0001-0001-0001-0001", identifier: 'Test Cell 1', family: "http://example.com/cell_families/1000-1000-1000-1000"},
  {uuid: "0002-0002-0002-0002", identifier: 'Test Cell 2', family: "http://example.com/cell_families/1000-1000-1000-1000"},
  {uuid: "0003-0003-0003-0003", identifier: 'Test Cell 3', family: "http://example.com/cell_families/2000-2000-2000-2000"},
]


it('renders', async () => {
  mockedAxios.request.mockResolvedValue({data: {results}});

  const queryClient = new QueryClient();

  render(
      <QueryClientProvider client={queryClient}>
        <ResourceList lookup_key={LOOKUP_KEYS.CELL} />
      </QueryClientProvider>
  )
  await screen.findByText(t => t.includes(results[0].uuid))

  expect(screen.getByRole('heading', {name: 'Cells'})).toBeInTheDocument();
  expect(screen.getAllByText(/ResourceCard/)).toHaveLength(3);
  expect(screen.getAllByText((c, e) => e instanceof HTMLElement && e.dataset.key === 'lookup_key')).toHaveLength(3);
})
