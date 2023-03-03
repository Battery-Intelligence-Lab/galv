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
 

