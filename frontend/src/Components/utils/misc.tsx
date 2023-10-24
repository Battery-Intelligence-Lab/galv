import {useParams} from "react-router-dom";

export type ObjectReferenceProps =
    { uuid: string } |
    { id: number } |
    { url: string }
export type ExpandableCardProps = ObjectReferenceProps & {
    expanded?: boolean
    editing?: boolean
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
    } catch (e) {
        throw new Error(`Could not parse id from url: ${url}: ${e}`)
    }
    console.error(`Could not parse id from props`, props)
    throw new Error(`Could not parse id from props`)
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