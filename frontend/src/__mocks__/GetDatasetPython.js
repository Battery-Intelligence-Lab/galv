// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import React from "react";

export default function DummyGetDatasetPython({dataset}) {
    return (
        <div>
            <p>GetDatasetPython</p>
            <p>{JSON.stringify({dataset})}</p>
        </div>
    )
}