// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

// Prevent complaints that 'spacing' isn't a DefaultTheme property
declare module "@mui/private-theming" {
  import type { Theme } from "@mui/material/styles";

  interface DefaultTheme extends Theme {}
}

declare module "@canvasjs/react-charts";