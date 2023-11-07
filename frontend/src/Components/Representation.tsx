import {API_HANDLERS, API_SLUGS, DISPLAY_NAMES, FIELDS, LookupKey, PRIORITY_LEVELS} from "../constants";
import {AxiosError, AxiosResponse} from "axios";
import {useQuery} from "@tanstack/react-query";
import {BaseResource} from "./ResourceCard";
import {ReactNode} from "react";

export function representation({data, lookup_key}: {data: any, lookup_key: LookupKey}): string {
    try {
        const id_fields = Object.entries(FIELDS[lookup_key])
            .filter(([k, v]) => v.priority >= PRIORITY_LEVELS.IDENTITY)
            .map(([k, v]) => k)

        const s = Object.entries(data)
            .filter(([k, v]) => id_fields.includes(k))
            .map(([k, v]) => v)
            .join(" ")

        return s.length? s : `${DISPLAY_NAMES[lookup_key]} ${data.uuid ?? data.id}`
    } catch (error) {
        console.error(`Could not represent ${lookup_key} ${data?.uuid ?? data?.id}`, {args: {data, lookup_key}, error})
    }
    return data.uuid ?? data.id ?? 'unknown'
}

export default function Representation<T extends BaseResource>({resource_id, lookup_key, prefix, suffix}: {
    resource_id: string|number
    lookup_key: LookupKey
    prefix?: ReactNode
    suffix?: ReactNode
}) {
    const api_handler = new API_HANDLERS[lookup_key]()
    const get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, resource_id],
        queryFn: () => get.bind(api_handler)(String(resource_id))
    })

    return <>
        {prefix ?? ""}
        {query.data? representation({data: query.data.data, lookup_key}) : resource_id}
        {suffix ?? ""}
    </>
}