// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React from "react";
import {MonitoredPathProps} from "../MonitoredPaths";

export default function DummyHarvesterDetail(props: MonitoredPathProps) {
  return (
    <div>
      <p>MockHarvesterDetail</p>
      <p>{JSON.stringify(props)}</p>
    </div>
  )
}
