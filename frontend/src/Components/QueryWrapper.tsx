import {UseQueryResult} from "@tanstack/react-query";
import {AxiosError, AxiosResponse} from "axios";

export type QueryDependentElement = (queries: UseQueryResult<AxiosResponse<any>, AxiosError>[]) => JSX.Element;

export type QueryWrapperProps = {
    queries: UseQueryResult<AxiosResponse<any>, AxiosError>[];
    loading: JSX.Element;
    error: QueryDependentElement | JSX.Element;
    success: QueryDependentElement | JSX.Element;
}

export default function QueryWrapper(props: QueryWrapperProps) {
    const loading = props.queries.some((query) => query.isLoading)
    const error = props.queries.some((query) => query.isError)
    const success = props.queries.every((query) => query.isSuccess)
    if (loading) return props.loading
    if (error)
        return typeof props.error === 'function' ?
            props.error(props.queries.filter((query) => query.isError)) : props.error
    if (success)
        return typeof props.success === 'function' ?
            props.success(props.queries.filter((query) => query.isSuccess)) : props.success
    throw new Error('QueryWrapper: fall-through case reached')
}