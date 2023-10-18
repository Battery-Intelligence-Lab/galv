import {UseQueryResult} from "@tanstack/react-query";
import {AxiosError, AxiosResponse} from "axios";

export type QueryDependentElement = (queries: UseQueryResult<AxiosResponse<any>, AxiosError>[]) => JSX.Element;

type QueryWrapperParams = {
    queries: UseQueryResult<AxiosResponse<any>, AxiosError>[];
    loading: JSX.Element;
    error: QueryDependentElement | JSX.Element;
    success: QueryDependentElement | JSX.Element;
}

export default function QueryWrapper(params: QueryWrapperParams) {
    const loading = params.queries.some((query) => query.isLoading)
    const error = params.queries.some((query) => query.isError)
    const success = params.queries.every((query) => query.isSuccess)
    if (loading) return params.loading
    if (error)
        return typeof params.error === 'function' ?
            params.error(params.queries.filter((query) => query.isError)) : params.error
    if (success)
        return typeof params.success === 'function' ?
            params.success(params.queries.filter((query) => query.isSuccess)) : params.success
    throw new Error('QueryWrapper: fall-through case reached')
}