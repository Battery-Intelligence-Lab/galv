// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React from "react";

const f = (v: any) => (props: any) => <div>
    <p>{v}</p>
    <p>{JSON.stringify(props)}</p>
</div>

export const PrettyString = f("PrettyString")
export const PrettyNumber = f("PrettyNumber")
export const PrettyBoolean = f("PrettyBoolean")
export const Pretty = f("Pretty")
export const Prettify = f("Prettify")

export default Prettify
