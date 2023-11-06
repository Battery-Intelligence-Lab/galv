import React, {createContext, PropsWithChildren} from "react";
import {Serializable, TypeChangerSupportedTypeName} from "../utils/TypeChanger";
import {FIELDS, LookupKey} from "../../constants";
import {useImmer} from "use-immer";

type FilterableData = {[key: string]: Serializable}
type FilterFunction = (value: Serializable, test_versus: any) => boolean
export type Filter = {key: string; family: FilterFamily; test_versus: any}

export type FilterableKeyType = TypeChangerSupportedTypeName & ("string"|"number"|"array")

export type FilterFamily = {
    name: string
    applies_to: readonly FilterableKeyType[]
    get_name: (filter: Filter, short_name: boolean) => string
    fun: FilterFunction
}

export const FILTER_FUNCTIONS: readonly FilterFamily[] = [
    {
        name: "equals",
        applies_to: ["string", "number"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ${filter.test_versus}` : `${filter.key} equals ${filter.test_versus}`,
        fun: (value, test_versus) => value === test_versus
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
        fun: (value, test_versus) => typeof value === "string" && value.startsWith(test_versus)
    },
    {
        name: "has substring",
        applies_to: ["string"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ...${filter.test_versus}...` : `${filter.key} has substring ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === "string" && value.includes(test_versus)
    },
    {
        name: "ends with",
        applies_to: ["string"],
        get_name: (filter, short_name) => short_name ?
            `${filter.key} = ...${filter.test_versus}` : `${filter.key} ends with ${filter.test_versus}`,
        fun: (value, test_versus) => typeof value === "string" && value.endsWith(test_versus)
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
}

export const FilterContext = createContext<IFilterContext>({
    activeFilters: Object.fromEntries(Object.keys(FIELDS)
        .map((k) => [k as LookupKey, {mode: FILTER_MODES.ALL, filters: [] as Filter[]}])) as ActiveFilters,
    setActiveFilters: () => {}
})

export function FilterContextProvider(props: PropsWithChildren<any>) {
    const [activeFilters, setActiveFilters] = useImmer<ActiveFilters>(
        Object.fromEntries(Object.keys(FIELDS).map((k) =>
            [k as LookupKey, {mode: FILTER_MODES.ALL, filters: [{key: "uuid", family: FILTER_FUNCTIONS[3], test_versus: "0"}] as Filter[]}]
        )) as ActiveFilters
    )

    return <FilterContext.Provider value={{activeFilters, setActiveFilters}}>
        {props.children}
    </FilterContext.Provider>
}
