import {API_ROOT} from "./conf.json"
import axios from "axios";
import {KnoxUser} from "./api_codegen";

axios.defaults.baseURL = API_ROOT.toLowerCase().replace(/\/+$/, '')
axios.defaults.headers.common['Accept'] = 'application/json'

const local_user_string = window.localStorage.getItem('user')
const user = JSON.parse(local_user_string || "{}")
if (user && user.token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${user.token}`
}

export const save_login_response = (user: KnoxUser) => {
    axios.defaults.headers.common['Authorization'] = `Bearer ${user.token}`
    window.localStorage.setItem('user', JSON.stringify(user))
}

export const id_from_url: (url: string) => string = (url: string) => {
    try {
        const id = url.split('/').filter(x => x).pop()
        if (id !== undefined) return id
    } catch (e) {
        throw new Error(`Could not parse id from url: ${url}: ${e}`)
    }
    throw new Error(`Could not parse id from url: ${url}`)
}