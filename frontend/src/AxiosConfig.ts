import {API_ROOT} from "./conf.json"
import axios from "axios";

axios.defaults.baseURL = API_ROOT.toLowerCase().replace(/\/+$/, '')
axios.defaults.headers.common['Accept'] = 'application/json'