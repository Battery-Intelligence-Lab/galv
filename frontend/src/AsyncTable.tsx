// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {Component, ReactElement, BaseSyntheticEvent, ReactEventHandler} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Connection, {APIObject, SingleAPIResponse} from "./APIConnection";
import TableRow from "@mui/material/TableRow";
import TableCell, {TableCellProps} from "@mui/material/TableCell";
import CircularProgress from "@mui/material/CircularProgress";
import Tooltip, {TooltipProps} from "@mui/material/Tooltip";
import Typography, {TypographyProps} from "@mui/material/Typography";
import TableHead from "@mui/material/TableHead";
import { withStyles } from "tss-react/mui";
import {type GridCellParams} from "@mui/x-data-grid";

export type Column = {
  label: string;
  help?: string;
  headerTableCellProps?: Partial<TableCellProps>;
  headerTooltipProps?: Partial<TooltipProps>;
  headerTypographyProps?: Partial<TypographyProps>;
  contentTableCellProps?: Partial<TableCellProps>;
}

export type RowGeneratorContext<T> = {
  columns: Column[];
  update: ReactEventHandler;
  update_direct: <K extends keyof T>(field_name: K, new_value: T[K]) => void;
  mark_loading: (state?: boolean) => void;
  refresh: (row_data: any) => void;
  refresh_from_api: () => void;
  refresh_all_rows: (use_cache?: boolean) => void;
  is_new_row: boolean;
  value_changed: boolean;
}

export type RowGenerator<T extends APIObject> =
  ((row_data: T) => ReactElement[]|null) |
  ((row_data: T, context: RowGeneratorContext<T>) => ReactElement[]|null)

type CompleteHeading = {
  label: string;
  help: string;
  tableCellProps: Partial<TableCellProps>;
  tooltipProps: Partial<TooltipProps>;
  typographyProps: Partial<TypographyProps>;
}

export type AsyncTableProps<T extends APIObject> = {
  classes: Record<any, string>;
  columns: Column[];
  row_generator: RowGenerator<T>;
  subrow?: JSX.Element;
  subrow_inclusion_rule?: (row_data: T) => boolean;
  url: string;
  new_row_values?: Partial<T>;
  styles?: any;
}

type AsyncTableState = {
  row_data: any[];
  new_row: any;
  loading: boolean;
  loading_rows: number[];
  changed_rows: number[];
}

export const NEW_ROW_ID = -1

/**
 * AsyncTable is designed to present data fetched from an API and allow
 * individual entries (rows) to be updated in isolation.
 *
 * AsyncTable takes an array of columns that define the headers and the
 * common row properties, and a functions that resolve into the an array of
 * contents of the TableCell elements in each TableRow in the body.
 *
 * The function that generates cell contents is passed the row data
 * and the context. `context` is a CellContext object that exposes
 * the column properties, and functions for updating local content
 * and for refreshing local content from the remote API.
 *
 * If `new_row_values` is specified, the row generator will be called
 * with those values to generate an extra row for adding new items.
 *
 * Data fetching is the responsibility of the AsyncTable via the
 * APIConnection class. It determines where to fetch data from
 * using the `initial_url` parameter.
 * - Updates to individual rows are the responsibility of the calling
 * code.
 * - Refreshing a row uses the row's `url` property to know where to look
 *
 * This class abstracts away a lot of repetitive table-building code.
 *
 * Subrows are used to display additional information about a row. They are
 * displayed when the subrow_inclusion_rule returns true for a row. The
 * usual use case for these is including another element such as a Harvester's
 * Monitored Paths.
 */
class AsyncTable<T extends APIObject> extends Component<AsyncTableProps<T>, AsyncTableState> {
  state: AsyncTableState = {
    row_data: [],
    new_row: null,
    loading: true,
    loading_rows: [],
    changed_rows: []
  }
  classes: Record<any, string>;


  constructor(props: AsyncTableProps<T>) {
    super(props)
    if (props.new_row_values !== undefined)
      this.state.new_row = this.new_row_template
    this.classes = withStyles.getClasses(this.props);
  }

  get new_row_template() {
    return {id: -1, url: "", ...this.props.new_row_values}
  }

  componentDidMount() {
    this.get_data(this.props.url)
    // console.log("Mounted AsyncTable", this)
  }

  componentDidUpdate(prevProps: AsyncTableProps<T>) {
    // console.log("Updating AsyncTable...", this, prevProps)
    // Typical usage (don't forget to compare props):
    if (this.props.url !== prevProps.url)
      this.get_data(this.props.url)
    if (this.props.new_row_values !== prevProps.new_row_values)
      this.reset_new_row()
    // console.log("Updated AsyncTable", this)
  }

  reset_new_row = () => this.setState({new_row: this.props.new_row_values? this.new_row_template : null})

  mark_row_loading = (row_id: number, status: boolean = true) => {
    const rows = this.state.loading_rows.filter(i => i !== row_id)
    if (status)
      rows.push(row_id)
    this.setState({loading_rows: rows})
  }

  mark_row_changed = (row_id: number, status: boolean = true) => {
    const rows = this.state.changed_rows.filter(i => i !== row_id)
    if (status)
      rows.push(row_id)
    this.setState({changed_rows: rows})
  }

  get_data: (url?: string, use_cache?: boolean) => void = (url, use_cache = true) => {
    this.setState({loading: true, row_data: []})
    if (!url)
      url = this.props.url;
    Connection.fetchMany(url, {}, !use_cache)
      .then((res) => {
        // console.log(res)
        this.setState({
          row_data: res.map(r => r.content),
          loading: false,
          loading_rows: [],
          changed_rows: []
        })
      })
      .catch(e => {
        console.error('Async Table error', e)
        this.setState({loading: false, loading_rows: []})
      })
  }

  refresh_row = (row: SingleAPIResponse, is_result: boolean = true) => {
    this.mark_row_loading(row.id)

    const _update = (row_data: SingleAPIResponse) => {
      this.setState({
        row_data: this.state.row_data.map(r => r.id === row.id ? row_data : r)
      })
      this.mark_row_changed(row.id, false)
      this.mark_row_loading(row.id, false)
    }

    if (is_result)
      return _update(row)

    Connection.fetch(row.url)
      .then(row_data => _update(row_data.content))
      .catch(e => {
        // If we deleted the row, delete it in state
        if (e.message === `Fetch failed for ${row.url}: 404`)
          this.setState({row_data: this.state.row_data.filter(r => r.id !== row.id)})
        else
          console.error('AsyncTable.update_single_row error', e, row)
      })
      .finally(
        () => this.mark_row_loading(row.id, false)
      )
  }

  update_all = async (use_cache: boolean = false) => {
    this.reset_new_row()
    return this.get_data(this.props.url, use_cache)
  }

  get header_row() {
    const column_headings: CompleteHeading[] = this.props.columns.map(
      (heading: Column) => ({
        label: heading.label,
        help: heading.help || "",
        tableCellProps: heading.headerTableCellProps || {},
        tooltipProps: heading.headerTooltipProps || {},
        typographyProps: heading.headerTypographyProps || {},
      })
    )

    return (
      <TableHead key="head">
        <TableRow>
          {column_headings.map((heading, i) =>
            <TableCell key={`${heading.label}_${i}`} {...heading.tableCellProps}>
              {
                <Tooltip title={heading.help} placement="top" {...heading.tooltipProps}>
                  <Typography {...heading.typographyProps}>
                    {heading.label}
                  </Typography>
                </Tooltip>
              }
            </TableCell>
          )}
        </TableRow>
      </TableHead>)
  }

  loading_row(id: number) {
    return <TableRow key={`loading-${id}`}>
      <TableCell colSpan={this.props.columns.length} align="center" aria-busy="true">
        <CircularProgress size="3rem"/>
      </TableCell>
    </TableRow>
  }

  row_conversion_context = (row: any, is_new_row: boolean) => {
    let update_fun: RowGeneratorContext<T>["update_direct"] = (name, value) => {
      this.setState({
        // Amend row_data to include new value for [name]
        row_data: this.state.row_data.map(r => r.id === row.id ? {...row, [name]: value} : r)
      })
      this.mark_row_changed(row.id)
    }
    if (is_new_row) {
      update_fun = (name, value) => {
        this.setState({new_row: {...this.state.new_row, [name]: value}})
        this.mark_row_changed(row.id)
      }
    }

    return {
      columns: this.props.columns,
      update: (event: BaseSyntheticEvent) => update_fun(event.target.name, event.target.value),
      update_direct: update_fun,
      mark_loading: (state: boolean = true) => this.mark_row_loading(row.id, state),
      refresh: (r: any) => this.refresh_row(r, true),
      refresh_from_api: () => this.refresh_row(row, false),
      refresh_all_rows: this.update_all,
      is_new_row,
      value_changed: this.state.changed_rows.includes(row.id)
    }
  }

  wrap_cells_in_row = (contents: ReactElement[], row_index: number) => {
    const cells = contents.map((cell: any, i: number) =>
      <TableCell
        {...this.props.columns[i].contentTableCellProps}
        className={[
          this.props.columns[i].contentTableCellProps?.className,
          row_index === NEW_ROW_ID? this.classes.newTableCell : undefined
        ].filter(n => n !== undefined).join(' ')}
        key={`cell-${i}`}
      >{cell}</TableCell>
    )
    return <TableRow
      key={`row-${row_index}`}
      className={row_index === NEW_ROW_ID? this.classes.newTableRow : undefined}
    >{cells}</TableRow>
  }

  get_subrow = (row: T, row_index: number, row_contents: (ReactElement|JSX.Element)[]) => {
    return (<TableRow key={`row-${row_index}-subrow`}>
        <TableCell colSpan={row_contents.length}>{this.props.subrow}</TableCell>
      </TableRow>)
  }

  row_data_to_tablerow = (row: T, row_index: number) => {
    try {
      if (!row)
        return null
      const is_new_row = row_index === NEW_ROW_ID
      if (is_new_row)
        row_index = -1

      if (this.state.loading_rows.includes(row.id))
        return this.loading_row(row.id)

      const row_contents = this.props.row_generator(row, this.row_conversion_context(row, is_new_row))
      if(!row_contents)
        return null
      const row_element = this.wrap_cells_in_row(row_contents, row_index)
      if (this.props.subrow_inclusion_rule && this.props.subrow_inclusion_rule(row))
        return [row_element, this.get_subrow(row, row_index, row_contents)]
      return row_element
    } catch(e) {
      console.info('Error constructing table row:', e)
      return null
    }
  }

  render() {
    return (
      <TableContainer>
        <Table className={this.props.styles?.table} size="small">
          {this.header_row}
          {
            <TableBody key="body">
              {this.state.loading && this.loading_row(-2)}
              {!this.state.loading && this.state.row_data.map(this.row_data_to_tablerow)}
              {
                !this.state.loading &&
                this.props.new_row_values !== undefined &&
                this.row_data_to_tablerow(this.state.new_row, NEW_ROW_ID)
              }
            </TableBody>
          }
        </Table>
      </TableContainer>
    )
  }
}

export type AsyncTableType<T extends APIObject> = typeof AsyncTable<T>

const StyledAsyncTable = withStyles(
  AsyncTable,
  (theme, props) => ({
    newTableRow: {},
    newTableCell: {},
  })
)

export default StyledAsyncTable