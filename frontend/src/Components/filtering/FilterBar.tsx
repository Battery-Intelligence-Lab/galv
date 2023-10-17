import React, {Component} from "react";
import Stack from "@mui/material/Stack";

export interface FilterWidgetProps<T> {
    filter_key: string
    filter: Filter<any>
    setFilterFn: (filterFn: (value: T) => boolean) => void
}

export type Filter<T> = {
    target_key: keyof T
    widget: typeof Component<FilterWidgetProps<T[keyof T]>>
    label?: string
}
type FilterBarProps<T> = {
    data: T[] | undefined
    filters: {[filter_key: string]: Filter<T>}
    setFilteredData: (filteredData: T[]) => void
}
type FilterBarState<T> = {
    filters: {[filter_key: string]: (value: T[keyof T]) => boolean}
}
export default class FilterBar<T> extends Component<FilterBarProps<T>, FilterBarState<T>> {
    state: FilterBarState<T> = {
        filters: {}
    }

    filter_data() {
        let data = this.props.data
        if (typeof data === 'undefined') return
        Object.entries(this.state.filters).forEach(([filter_key, filter_value]) => {
            const filter = this.props.filters[filter_key]
            data = data?.filter((datum) => filter_value(datum[filter.target_key]))
        })
        this.props.setFilteredData(data)
    }

    componentDidUpdate(prevProps: Readonly<FilterBarProps<T>>, prevState: Readonly<FilterBarState<T>>, snapshot?: any) {
        if (prevProps.data !== this.props.data) {
            this.filter_data()
        }
    }

    render() {
        return <Stack direction="row" spacing={2}>
            {Object.entries(this.props.filters).map(([filter_key, filter]) =>
                <filter.widget key={filter_key} filter_key={filter_key} filter={filter} setFilterFn={(filterFn) => {
                    this.setState({filters: {...this.state.filters, [filter_key]: filterFn}} as FilterBarState<T> )
                    this.filter_data()
                }}/>
            )}
        </Stack>
    }
}