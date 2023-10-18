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
    const url = typeof props === 'string' ? props : props.url
    try {
        const id = url.split('/').filter(x => x).pop()
        if (id !== undefined) return id as T
    } catch (e) {
        throw new Error(`Could not parse id from url: ${url}: ${e}`)
    }
    throw new Error(`Could not parse id from url: ${url}`)
}