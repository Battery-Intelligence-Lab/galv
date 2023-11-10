import React, {createContext, PropsWithChildren, useEffect, useState} from "react";
import {Serializable, TypeChangerSupportedTypeName} from "../TypeChanger";
import {FAMILY_LOOKUP_KEYS, FIELDS, get_has_family, LookupKey} from "../../constants";
import {useImmer} from "use-immer";
import {IApiResourceContext} from "../ApiResourceContext";

type FilterFunction = (value: Serializable, test_versus: any) => boolean
export type Filter = {key: string; family: FilterFamily; test_versus: any}

export type FilterableKeyType = TypeChangerSupportedTypeName & ("boolean"|"string"|"number"|"array")

export type FilterFamily = {
    name: string
    applies_to: readonly FilterableKeyType[]
    get_name: (filter: Filter, short_name: boolean) => string
    fun: FilterFunction
}

const value_to_string = (value: Serializable): string => {
    return (value instanceof Object && "value" in value)? value.value as string : String(value)
}

export const FILTER_FUNCTIONS: readonly FilterFamily[] = [
    {
        name: "is",
        applies_to: ["string", "number", "boolean"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ${filter.test_versus}` : `${filter.key} is ${filter.test_versus}`,
        fun: (value, test_versus) => {
            switch(typeof value) {
                case "string": return value_to_string(value) === String(test_versus)
                case "number": return value === Number(test_versus)
                case "boolean": return value === Boolean(test_versus)
            }
            console.error(`Cannot compare ${typeof value} to ${typeof test_versus}`, value, test_versus)
            throw new Error(`'is' filter can only be used for strings, numbers, and booleans`)
        }
    },
    {
        name: "includes",
        applies_to: ["array"],
        get_name: (filter, short_name) => short_name ?
            `${filter.test_versus} ∈ ${filter.key}` : `${filter.key} includes ${filter.test_versus}`,
        fun: (value, test_versus) => value instanceof Array && value.includes(test_versus)
    },
    {
        name: "starts with",
        applies_to: ["string"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ${filter.test_versus}...` : `${filter.key} starts with ${filter.test_versus}`,
        fun: (value, test_versus) =>
            typeof value_to_string(value) === "string" && value_to_string(value).startsWith(test_versus)
    },
    {
        name: "has substring",
        applies_to: ["string"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ...${filter.test_versus}...` : `${filter.key} has substring ${filter.test_versus}`,
        fun: (value, test_versus) =>
            typeof value_to_string(value) === "string" && value_to_string(value).includes(test_versus)
    },
    {
        name: "ends with",
        applies_to: ["string"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ...${filter.test_versus}` : `${filter.key} ends with ${filter.test_versus}`,
        fun: (value, test_versus) =>
            typeof value_to_string(value) === "string" && value_to_string(value).endsWith(test_versus)
    },
    {
        name: "less than",
        applies_to: ["number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} < ${filter.test_versus}` : `${filter.key} less than ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === 'number' && value < test_versus
    },
    {
        name: "greater than",
        applies_to: ["number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} > ${filter.test_versus}` : `${filter.key} greater than ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === 'number' && value > test_versus
    },
    {
        name: "less than or equal to",
        applies_to: ["number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} <= ${filter.test_versus}` : `${filter.key} less than or equal to ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === 'number' && value <= test_versus
    },
    {
        name: "greater than or equal to",
        applies_to: ["number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} >= ${filter.test_versus}` : `${filter.key} greater than or equal to ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === 'number' && value >= test_versus
    },
    {
        name: "not equal to",
        applies_to: ["number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} != ${filter.test_versus}` : `${filter.key} not equal to ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === 'number' && value !== test_versus
    }
] as const

export type FilterMode = "ANY"|"ALL"
export const FILTER_MODES = {
    ANY: "ANY",
    ALL: "ALL"
} as const

export type ActiveFilters = {
    [key in LookupKey]: { mode: FilterMode, filters: Filter[] }
};

export interface IFilterContext {
    activeFilters: ActiveFilters
    setActiveFilters: (filters: ActiveFilters) => void
    passesFilters: (data: IApiResourceContext, lookup_key: LookupKey) => boolean
}

export const FilterContext = createContext<IFilterContext>({
    activeFilters: Object.fromEntries(Object.keys(FIELDS)
        .map((k) => [k as LookupKey, {mode: FILTER_MODES.ALL, filters: [] as Filter[]}])) as ActiveFilters,
    setActiveFilters: () => {},
    passesFilters: () => true
})

export function FilterContextProvider(props: PropsWithChildren<any>) {
    const [activeFilters, setActiveFilters] = useImmer<ActiveFilters>(
        Object.fromEntries(Object.keys(FIELDS).map((k) =>
            [k as LookupKey, {mode: FILTER_MODES.ALL, filters: [] as Filter[]}]
        )) as ActiveFilters
    )

    const [passesFilters, setPassesFilters] =
        useState<(data: IApiResourceContext, lookup_key: LookupKey) => boolean>(() => () => true)

    useEffect(() => {
        setPassesFilters(() => (data: IApiResourceContext, lookup_key: LookupKey) => {
            if (data.apiResource === undefined) return true
            const family_lookup_key = get_has_family(lookup_key) ? FAMILY_LOOKUP_KEYS[lookup_key] : undefined
            const filter_mode = activeFilters[lookup_key].mode === FILTER_MODES.ANY? "some" : "every"
            // if there are no filters, everything passes
            return (
                activeFilters[lookup_key].filters.length === 0 &&
                (!family_lookup_key || activeFilters[family_lookup_key].filters.length === 0)
            ) || (
                // the resource has to pass its filters
                activeFilters[lookup_key].filters[filter_mode](
                    f => f.family.fun(data.apiResource?.[f.key], f.test_versus)
                ) && (
                    // if the resource has a family, that has to pass its filters, too
                    !family_lookup_key || activeFilters[family_lookup_key].filters[filter_mode](
                        f => f.family.fun(data.family?.[f.key], f.test_versus)
                    )
                )
            )
        })
    }, [activeFilters])

    return <FilterContext.Provider value={{activeFilters, setActiveFilters, passesFilters}}>
        {props.children}
    </FilterContext.Provider>
}
