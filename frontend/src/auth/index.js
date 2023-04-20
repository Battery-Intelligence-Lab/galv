// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galvanalyser' Developers. All rights reserved.

import {createAuthProvider} from 'react-token-auth';


export const [useAuth, authFetch, login, logout] =
    createAuthProvider({
        accessTokenKey: 'access_token',
        onUpdateToken: (token) => fetch(
          '/api-auth/refresh', {
            method: 'POST',
            body: token.access_token,
            headers: {'Content-Type': 'application/json'}
          }
        ).then((response) => {
          if (response.ok) {
            console.log('refresh good');
            return response.json();
          }
          console.log('refresh failed');
        })
    });
