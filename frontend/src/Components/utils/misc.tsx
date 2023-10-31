import {useParams} from "react-router-dom";
import {Serializable} from "./TypeChanger";
import {API_HANDLERS, PATHS} from "../../constants";

export type ObjectReferenceProps =
    { uuid: string } |
    { id: number } |
    { url: string }
export type ExpandableCardProps = ObjectReferenceProps & {
    expanded?: boolean
    editing?: boolean
}
export type PaginatedAPIResponse<T = any> = {
    count: number
    next: string | null
    previous: string | null
    results: T[]
}

export function id_from_ref_props<T extends number | string>(props: ObjectReferenceProps | string | number): T {
    if (typeof props === 'number')
        return props as T
    if (typeof props === 'object') {
        if ('uuid' in props) {
            return props.uuid as T
        } else if ('id' in props) {
            return props.id as T
        }
    }
    const url = typeof props === 'string' ? props : props?.url
    try {
        const id = url.split('/').filter(x => x).pop()
        if (id !== undefined) return id as T
    } catch (error) {
        console.error(`Could not parse id from url`, {props, url, error})
        throw new Error(`Could not parse id from url.`)
    }
    console.error(`Could not parse id from props`, props)
    throw new Error(`Could not parse id from props ${props}`)
}

/**
 * Get the id from the props (first choice) or the router params (second choice)
 * @param props
 */
export function usePropParamId<T extends number|string>(props: any): T {
    const params = useParams()
    const param_id = (params.uuid || params.id) as T
    if (["string", "number"].includes(typeof props) ||
        (typeof props === 'object' && ('uuid' in props || 'id' in props || 'url' in props))) {
        return id_from_ref_props<T>(props)
    }
    if (param_id === undefined) {
        console.error(`Could not find id from props or params`, props, params)
        throw new Error(`Could not find id from props or params`)
    }
    return param_id
}

/**
 * If `url` looks like a valid url for a resource, return the lookup key and uuid.
 * @param url
 */
export function get_url_components(url: string):
    {lookup_key: keyof typeof API_HANDLERS & string,
        uuid: string}|undefined {
    url = url.toLowerCase()
    const parts = url.split(/[/|?]/).filter(x => x)
    if (parts.length === 4) {
        const lookup_key = Object.keys(PATHS)
            .find(k => PATHS[k as keyof typeof PATHS] === `/${parts[2]}`)
        if (lookup_key === undefined) return undefined

        if (!Object.keys(API_HANDLERS).includes(lookup_key)) {
            console.warn(`${lookup_key} is a PATHS key but not an API_HANDLERS key`, url)
            return undefined
        }

        const uuid = parts[3]
        return {lookup_key: lookup_key as keyof typeof API_HANDLERS, uuid}
    }
    return undefined
}

export function build_placeholder_url(lookup_key: keyof typeof PATHS & string, uuid: string = 'new') {
    return `https://galv${PATHS[lookup_key]}/${uuid}`
}

export function deep_copy<T extends Serializable>(obj: T): T {
    return JSON.parse(JSON.stringify(obj))
}