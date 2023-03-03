// Prevent complaints that 'spacing' isn't a DefaultTheme property
declare module "@mui/private-theming" {
  import type { Theme } from "@mui/material/styles";

  interface DefaultTheme extends Theme {}
}