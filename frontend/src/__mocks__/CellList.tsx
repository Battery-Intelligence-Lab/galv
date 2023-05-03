// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React from "react";
import {CellDetailProps} from "../CellList";

export default function DummyCellList(props: CellDetailProps) {
  return (
    <div>
      <p>CellList</p>
      <p>{JSON.stringify(props)}</p>
    </div>
  )
}
