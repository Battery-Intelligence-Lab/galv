// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React from "react";

export default function DummyRepresentation({params}: any) {
    return (
        <div>
            <p>Representation</p>
            <p>{JSON.stringify({params})}</p>
        </div>
    )
}
