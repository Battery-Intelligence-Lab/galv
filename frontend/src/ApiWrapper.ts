
import {API_ROOT} from "./conf.json"
import {Configuration, ConfigurationParameters} from "./api_codegen";
import {BaseAPI} from "./api_codegen/base";
import {AxiosInstance} from "axios";

export const get_api_config: (config?: ConfigurationParameters) => Configuration = (config) => {
    const local_user_string = window.localStorage.getItem('user')
    const user = JSON.parse(local_user_string || "{}")
    return new Configuration({
        'basePath': API_ROOT.toLowerCase().replace(/\/+$/, ''),
        ...user,
        ...config
    })
}

function factory<T>(type: { new (): T }): T {
    return new type();
}

export function get_api_handler<T extends BaseAPI>(
    api_client_class: { new (configuration?: Configuration | undefined, basePath?: string, axios?: AxiosInstance): T},
    config?: ConfigurationParameters
): T {
    return new api_client_class(get_api_config(config))
}
