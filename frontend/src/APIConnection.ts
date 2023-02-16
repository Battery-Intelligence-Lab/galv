export type User = {
  url: string,
  id: number,
  username: string,
  first_name: string,
  last_name: string,
  is_staff: boolean,
  is_superuser: boolean,
  token: string,
}

export interface APIObject {
  id: number;
  url: string;
}
export type SingleAPIResponse = APIObject & {[prop: string]: any}
export type MultipleAPIResponse = SingleAPIResponse[]
export type PaginatedAPIResponse = {
  count: number, previous?: string, next?: string, results: SingleAPIResponse[]
}
export type ErrorCode = number

export type APIResponse = SingleAPIResponse |
  MultipleAPIResponse |
  PaginatedAPIResponse |
  ErrorCode

export type CachedAPIResponse<T extends SingleAPIResponse> = {
  url: string;
  time: Date;
  content: T;
  loading: boolean;
  parents: string[];
}

function clean_url(url: string, baseURL: string): string {
  url = url.toLowerCase();
  if (!url.startsWith(baseURL))
    url = `${baseURL}${url}`
  return url
}

class ResponseCache {
  results: CachedAPIResponse<any>[]
  url: string

  constructor(url: string) {
    this.url = url
    this.results = []
  }

  add<T extends SingleAPIResponse>(item: T | T[], parent: string = "") {
    if (item instanceof Array)
      item.forEach(i => this.add(i, parent))
    else
      try {
        const i = this.results.find(i => i.url === item.url)
        const parents = i? i.parents.filter(p => p !== parent) : []
        this.results = [
          ...this.results.filter(i => i.url !== item.url),
          {
            url: item.url,
            time: new Date(),
            content: item,
            loading: false,
            parents: parent? [...parents, parent] : parents
          }
        ]
      } catch (e) {
        console.error(e)
      }
  }

  remove(url: string) {
    url = clean_url(url, this.url)
    this.results = this.results.filter(i => i.url !== url)
  }

  get<T extends SingleAPIResponse>(url: string, include_children: boolean = true): CachedAPIResponse<T>[] {
    url = clean_url(url, this.url)
    return this.results.filter(i => i.url === url || (include_children && i.parents.includes(url)))
  }

  get_contents<T extends SingleAPIResponse>(url: string, include_children: boolean = true) {
    url = clean_url(url, this.url)
    return this.get<T>(url, include_children).map(r => r.content)
  }
}

export class APIConnection {
  url: string = 'http://localhost:5000/'.toLowerCase()
  user: User | null = null
  cache_expiry_time = 60_000 // 1 minute
  results: ResponseCache

  constructor() {
    console.info("Spawn API connection")
    this.login('admin', 'admin');
    console.log(document.cookie)
    this.results = new ResponseCache(this.url)
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
        return true
      })
      .catch(e => {
        console.error("Login failure", e)
        return false
      })
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

  get is_logged_in() {
    return !!this.user?.token
  }

  async get_is_logged_in(skip: boolean = true): Promise<boolean> {
    await this.login('admin', 'admin')
    const cookie = this.get_cookie('csrf_access_token');
    if (cookie === undefined || !this.user)
      if (!skip)
        return this.get_is_logged_in(false);
    return cookie !== undefined && this.user !== null;
  }

  _prepare_fetch_headers(url: string, options?: any) {
    if (!this.is_logged_in)
      throw new Error(`Cannot fetch ${url}: not logged on.`)
    console.info(`Fetch ${url} for ${this.user?.username}`, options)
    // console.info('fetch options', options)
    const token = this.user?.token;
    let newOptions = {...options};
    newOptions.credentials = 'same-origin';
    newOptions.headers = {...newOptions.headers};
    newOptions.headers['Content-Type'] = "application/json";
    newOptions.headers['Accept'] = "application/json";
    newOptions.headers['Authorization'] = `Bearer ${token}`;
    // newOptions.headers['X-CSRF-TOKEN'] = this.get_cookie('csrf_access_token');
    return newOptions;
  }

  _fetch<T extends SingleAPIResponse>(url: string, options: object, parent: string = ""): Promise<void> {
    return fetch(url, options)
      .then((response) => {
        if (response.status >= 400) {
          console.error(response)
          if (response.status === 404)
            this.results.remove(url)
          throw new Error(`Fetch failed for ${url}: ${response.status}`)
        }
        return response.json() as Promise<T|T[]>;
      })
      .then(json => this.results.add<T>(json, parent))
  }

  async fetchMany<T extends SingleAPIResponse>(url: string, options?: any, ignore_cache: boolean = true): Promise<CachedAPIResponse<T>[]> {
    url = clean_url(url, this.url)
    const newOptions = this._prepare_fetch_headers(url, options);
    if (newOptions.method && newOptions.method.toLowerCase() !== 'get')
      ignore_cache = true;
    // Check cache
    if (!ignore_cache) {
      const results = this.results.get(url)
      if (!results.length)
        return this.fetchMany(url, options, true)
      const now = new Date()
      let fetch = results.filter(r => now.valueOf() - r.time.valueOf() > this.cache_expiry_time)
      fetch.forEach(r => r.loading = true)
      await Promise.all(fetch.map(r => this.fetch(r.url, options, ignore_cache = true)))
      return this.results.get(url)
    }
    return this._fetch<T>(url, newOptions, url)
      .then(() => this.results.get<T>(url))
  }

  async fetch<T extends SingleAPIResponse>(url: string, options?: any, ignore_cache = false): Promise<CachedAPIResponse<T>> {
    url = clean_url(url, this.url)
    const newOptions = this._prepare_fetch_headers(url, options);
    if (newOptions.method && newOptions.method.toLowerCase() !== 'get')
      ignore_cache = true;
    // Check cache
    if (!ignore_cache) {
      const results = this.results.get<T>(url)
      if (!results.length || new Date().valueOf() - results[0].time.valueOf() > this.cache_expiry_time) {
        if (results.length)
          results[0].loading = true
        return this.fetch(url, options, true)
      }
      return results[0]
    }
    return this._fetch<T>(url, newOptions)
      .then(() => this.results.get<T>(url)[0])
  }
}

const Connection = new APIConnection();
export default Connection;