import {API_HANDLERS, API_SLUGS, GET_REPRESENTATIONS} from "../../constants";
import {AxiosError, AxiosResponse} from "axios";
import {useQuery} from "@tanstack/react-query";
import {BaseResource} from "./ResourceCard";

export default function Representation<T extends BaseResource>({resource_id, lookup_key}: {
    resource_id: string|number,
    lookup_key: keyof typeof GET_REPRESENTATIONS
}) {
    const api_handler = new API_HANDLERS[lookup_key]()
    const get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, resource_id],
        queryFn: () => get.bind(api_handler)(String(resource_id))
    })
    return query.data ? GET_REPRESENTATIONS[lookup_key](query.data.data) : resource_id
}