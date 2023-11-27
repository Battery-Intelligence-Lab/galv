// // SPDX-License-Identifier: BSD-2-Clause
// // Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// // of Oxford, and the 'Galv' Developers. All rights reserved.

// globalThis.IS_REACT_ACT_ENVIRONMENT = true;

import {LOOKUP_KEYS} from "../constants";
import React from 'react';
import { act, render, screen } from '@testing-library/react';
import axios from 'axios';
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";

// Mock jest and set the type
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

const Representation = jest.requireActual('../Components/Representation').default;

it('Representation renders', async () => {
  mockedAxios.get.mockResolvedValue({
    data: {
      id: 1,
      name: 'Joe Doe'
    }
  });

  const queryClient = new QueryClient();

  await act(async () => render(
      <QueryClientProvider client={queryClient}>
        <Representation lookup_key={LOOKUP_KEYS.TEAM} resource_id={1} />
      </QueryClientProvider>
  ));
  screen.debug();
})
