// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React from "react";
import {HarvesterEnvProps} from "../HarvesterEnv";

export default function DummyHarvesterEnv(props: HarvesterEnvProps) {
  return (
    <div>
      <p>MockHarvesterEnv</p>
      <p>{JSON.stringify(props)}</p>
    </div>
  )
}
