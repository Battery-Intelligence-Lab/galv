// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

/*
* Theme wrapper for the app. Body in Core.tsx
*/

import React from "react";
import { createTheme, StyledEngineProvider } from '@mui/material/styles';
import { ThemeProvider } from "@mui/styles";
import Core from "./Core.tsx"

const theme = createTheme();

export default function App() {
  return (
      <ThemeProvider theme={theme}>
        <StyledEngineProvider injectFirst>
          <Core/>
        </StyledEngineProvider>
      </ThemeProvider>
  );
}
 

