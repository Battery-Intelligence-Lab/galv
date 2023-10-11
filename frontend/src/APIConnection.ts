// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import {API_ROOT} from "./conf.json"

export type User = {
  url: string;
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  token: string;
}

export interface APIObject {
  id?: number;
  uuid?: string;
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

export type APIMessage = {
  severity: "error" | "warning" | "info" | "success";
  message: string;
  context?: any;
}

export type MessageHandler = (message: APIMessage) => void

export type ConnectionProps = {
  base_url?: string;
  message_handlers?: MessageHandler[];
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

  purge(parent: string) {
    if (parent === '')
      throw new Error(`You have passed an empty string to ResponseCache.remove.
      This is likely a mistake and results will not be removed.`)
    this.results = this.results.filter(r => !r.parents.includes(parent))
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

/**
 * @class
 * APIConnection manages a connection to the backend REST API.
 * It handles user management directly, and offers a modified
 * fetch interface for everything else.
 *
 * Results are cached and can be referenced directly with their
 * canonical URL and indirectly with a parent URL.
 */
export class APIConnection {
  url: string = API_ROOT.toLowerCase()
  user: User | null = null
  cache_expiry_time = 60_000 // 1 minute
  results: ResponseCache
  cookies: any
  message_handlers: MessageHandler[] = []

  constructor(props?: ConnectionProps) {
    if (props?.base_url)
      this.url = props.base_url
    if (props?.message_handlers)
      this.message_handlers = props.message_handlers
    // console.info(`Spawn API connection (${this.url})`)
    const local_user = window.localStorage.getItem('user')
    if (local_user)
      this.user = JSON.parse(local_user)
    this.results = new ResponseCache(this.url)
  }

  create_user(username: string, email: string, password: string): Promise<User> {
    return fetch(
      this.url + 'inactive_users/',
      {
        method: 'POST',
        headers: {accept: 'application/json', 'content-type': 'application/json'},
        body: JSON.stringify({username, email, password})
      }
    )
      .then(r => {
        if (r.status !== 200)
          return r.json().then(json => {throw new Error(json.error)})
        return r.json()
      })
  }

  update_user(email: string, password: string, currentPassword: string): Promise<APIMessage> {
    if (!this.user)
      return new Promise(() => {})
    return fetch(
      this.user.url,
      {
        method: 'PATCH',
        headers: {
          'content-type': 'application/json',
          accept: 'application/json',
          authorization: `Bearer ${this.user.token}`
        },
        body: JSON.stringify({email, password, currentPassword})
      }
    )
      .then(r => {
        if (r.status === 200)
          return r.json()
            .then(user => {
              this.user = {...user, token: this.user?.token}
            })
            .then(() => ({severity: "success", message: 'Updated successfully'}))
        return r.json()
          .then(r => ({severity: "error", message: r.error}))
      })
  }

  login(username: string, password: string) {
    let headers = new Headers();
    headers.set('Authorization', 'Basic ' + btoa(username + ":" + password));
    headers.set('Accept', 'application/json');
    return fetch(this.url + 'login/', {method: 'POST', headers: headers})
      .then(r => r.json())
      .then(user => {
        this.user = user
        window.localStorage.setItem('user', JSON.stringify(this.user))
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
    window.localStorage.removeItem('user')
    return fetch(this.url + "logout/", {method: 'POST'})
  }

  get is_logged_in() {
    return !!this.user?.token
  }

  _prepare_fetch_headers(url: string, options?: any) {
    if (!this.is_logged_in)
      throw new Error(`Cannot fetch ${url}: not logged on.`)
    console.info(`Fetch ${url} for ${this.user?.username}`, options)
    // console.info('fetch options', options)
    const token = this.user?.token;
    let newOptions = {...options};
    newOptions.headers = {...newOptions.headers};
    newOptions.headers['Content-Type'] = "application/json";
    newOptions.headers['Accept'] = "application/json";
    newOptions.headers['Authorization'] = `Bearer ${token}`;
    return newOptions;
  }

  _fetch<T extends SingleAPIResponse>(url: string, options: object, parent: string = "", void_cache: boolean = false): Promise<string> {
    return fetch(url, options)
      .then((response) => {
        if (response.status >= 400) {
          console.error(response)
          if (response.status === 401)
            return this.logout().then(() => {
              throw new Error(`Logged out: not authorized to access ${url}`)
            })
          if (response.status === 404)
            this.results.remove(url)
          try {
            return response.json().then(j => {
              if (j.error)
                throw new Error(`Server error: ${j.error}`)
              throw new Error(`Fetch failed for ${url}: ${response.status}`)
            })
          } catch (e) {
            throw new Error(`Fetch failed for ${url}: ${response.status}`)
          }
        }
        if (response.status === 204)
          return null;
        return response.json() as Promise<T|T[]>;
      })
      .catch(e => {
        this.message_handlers.forEach(h => h({severity: "error", message: e.message, context: e}))
        return url
      })
      .then(json => {
        if (void_cache)
          this.results.purge(parent)
        if (typeof json === "string")
          return json
        if (json === null) {
          this.results.remove(url)
          return url
        }
        this.results.add<T>(json, parent)
        return json instanceof Array? parent : json.url
      })
  }

  async fetchRaw<T>(url: string, options?: any): Promise<T> {
    url = clean_url(url, this.url)
    const newOptions = this._prepare_fetch_headers(url, options);
    return fetch(url, newOptions)
      .then((response) => response.body as T)
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
    return this._fetch<T>(url, newOptions, url, ignore_cache)
      .then((result_url) => this.results.get<T>(result_url))
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
      .then((result_url) => this.results.get<T>(result_url)[0])
  }
}

const Connection = new APIConnection();
export default Connection;