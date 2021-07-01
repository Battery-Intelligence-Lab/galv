import {createAuthProvider} from 'react-token-auth';


export const [useAuth, authFetch, login, logout] =
    createAuthProvider({
        accessTokenKey: 'access_token',
        onUpdateToken: (token) => fetch(
          '/api/refresh', {
            method: 'POST',
            body: token.access_token
          }
        ).then((response) => {
          if (response.ok) {
            console.log('refresh good');
            return response.json();
          }
          console.log('refresh failed');
        })
    });
