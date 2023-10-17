import React, {Component} from "react";
import TextField from "@mui/material/TextField";
import {Filter, FilterWidgetProps} from "./FilterBar";

type TextFilterProps = FilterWidgetProps<string> & {}

export default class TextFilter extends Component<TextFilterProps> {
    render() {
        return <TextField key={this.props.filter_key} label={this.props.filter.label} type="search" variant="outlined" onChange={(e) => {
            this.props.setFilterFn((d) => (d as string).search(e.target.value) !== -1)
        }}/>
    }
}