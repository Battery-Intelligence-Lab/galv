export type User = {
  url: string,
  id: number,
  username: string,
  first_name: string,
  last_name: string,
  is_staff: boolean,
  is_superuser: boolean,
  // groups: {
  //   url: string,
  //   name: string,
  //   permissions: []
  // }[],
  token: string,
}

export type SingleAPIResponse = any
export type MultipleAPIResponse = SingleAPIResponse[]
export type PaginatedAPIResponse = {
  count: number, previous?: string, next?: string, results: SingleAPIResponse[]
}
export type ErrorCode = number

export type APIResponse = SingleAPIResponse |
  MultipleAPIResponse |
  PaginatedAPIResponse |
  ErrorCode

export class APIConnection {
  url: string = 'http://localhost:5000/'.toLowerCase()
  user: User | null = null
  results: { [result_name: string]: APIResponse }

  constructor() {
    console.info("Spawn API connection")
    this.login('admin', 'admin');
    this.results = {}
  }

  login(username: string, password: string) {
    let headers = new Headers();
    headers.set('Authorization', 'Basic ' + btoa(username + ":" + password));
    headers.set('Accept', 'application/json');
    return fetch(this.url + 'login/', {method: 'POST', headers: headers})
      .then(r => r.json())
      .then(r => {
        this.user = {
          ...r.user,
          token: r.token
        }
        console.info(`Logged in as ${this.user?.username}`)
      })
      .catch(e => console.error("Login failure", e))
  }

  logout() {
    this.user = null
    return fetch(this.url + "logout/", {method: 'POST'})
  }

  get_cookie(name: string) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts?.pop()?.split(';').shift();
    return null
  }

  async get_is_logged_in(skip: boolean = true): Promise<boolean> {
    await this.login('admin', 'admin')
    const cookie = this.get_cookie('csrf_access_token');
    if (cookie === undefined || !this.user)
      if (!skip)
        return this.get_is_logged_in(false);
    return cookie !== undefined && this.user !== null;
  }

  async fetch(url: string, options?: any, cache_name: string = ""): Promise<APIResponse> {
    await this.get_is_logged_in();
    console.info(`Fetch ${url} for ${this.user?.username}`)
    console.info('fetch options', options)
    const token = this.user?.token;
    let newOptions = {...options};
    newOptions.credentials = 'same-origin';
    newOptions.headers = {...newOptions.headers};
    newOptions.headers['Content-Type'] = "application/json";
    newOptions.headers['Accept'] = "application/json";
    newOptions.headers['Authorization'] = `Token ${token}`;
    newOptions.headers['X-CSRF-TOKEN'] = this.get_cookie('csrf_access_token');
    url = url.toLowerCase();
    if (!url.startsWith(this.url))
      url = `${this.url}${url}`;
    return fetch(url, newOptions)
      .then((response) => {
        if (response.status === 401) {
          throw new Error(`Authorisation failed while fetching ${url}`)
          // return logout().then(() => {
          //   return response;
          // });
        }
        if (response.status === 404)
          return 404;
        return response.json();
      })
      .catch(e => {
        console.error(e);
        return {
          count: 0,
          previous: null,
          next: null,
          results: [],
          error: true
        };
      });
  }

  static get_result_array: (r: APIResponse) => MultipleAPIResponse = r => {
    if (r instanceof Array)
      return r;
    if (r.results !== undefined)
      return r.results;
    return r;
  }
}

const Connection = new APIConnection();
export default Connection;