import React, {Component, ReactElement, Fragment, BaseSyntheticEvent, ReactEventHandler} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Connection, {APIConnection, APIResponse, SingleAPIResponse} from "./APIConnection";
import TableRow from "@mui/material/TableRow";
import TableCell, {TableCellProps} from "@mui/material/TableCell";
import CircularProgress from "@mui/material/CircularProgress";
import Tooltip, {TooltipProps} from "@mui/material/Tooltip";
import Typography, {TypographyProps} from "@mui/material/Typography";
import TableHead from "@mui/material/TableHead";

export type Column = {
  label: string;
  help?: string;
  headerTableCellProps?: Partial<TableCellProps>;
  headerTooltipProps?: Partial<TooltipProps>;
  headerTypographyProps?: Partial<TypographyProps>;
  contentTableCellProps?: Partial<TableCellProps>;
}

export type CellContext = {
  column_properties: Column;
  update: ReactEventHandler;
  refresh: () => void;
  refresh_all_rows: () => void;
}

export type Cell = ReactElement |
  ((row_data: any) => ReactElement) |
  ((row_data: any, context: CellContext) => ReactElement)

type CompleteHeading = {
  label: string;
  help: string;
  tableCellProps: Partial<TableCellProps>;
  tooltipProps: Partial<TooltipProps>;
  typographyProps: Partial<TypographyProps>;
}

export type AsyncTableProps = {
  columns: Column[];
  rows: Cell[];
  initial_url: string;
  new_entry_row?: Cell[];
  new_row_values?: any;
  styles?: any;
  [key: string]: any;
}

type AsyncTableState = {
  row_data: any[];
  new_row: any;
  last_updated: Date;
  loading: boolean;
  loading_rows: number[];
}

/**
 * AsyncTable is designed to present data fetched from an API and allow
 * individual entries (rows) to be updated in isolation.
 *
 * AsyncTable takes an array of columns that define the headers and the
 * common row properties, and an array of elements or functions that
 * resolve into the contents of the TableCell elements in each TableRow
 * in the body.
 *
 * The functions that generate cell contents are passed the row data
 * and the context. `context` is a CellContext object that exposes
 * the column properties, and functions for updating local content
 * and for refreshing local content from the remote API.
 *
 * Data fetching is the responsibility of the AsyncTable via the
 * APIConnection class. It determines where to fetch data from
 * using the `initial_url` parameter.
 * - Updates to individual rows are the responsibility of the calling
 * code.
 * - Refreshing a row uses the row's `url` property to know where to look
 *
 * This class abstracts away a lot of repetitive table-building code.
 */
export default class AsyncTable extends Component<AsyncTableProps, AsyncTableState> {
  current_url: string = "";

  state: AsyncTableState = {
    row_data: [],
    new_row: null,
    last_updated: new Date(0),
    loading: true,
    loading_rows: []
  }

  constructor(props: AsyncTableProps) {
    if (props.columns.length !== props.rows.length)
      throw new Error(`Length of rows (${props.rows.length}) must match number of columns (${props.columns.length})`)
    if (props.new_entry_row !== undefined && props.columns.length !== props.new_entry_row?.length)
      throw new Error(`Length of new_entry_row (${props.new_entry_row.length}) must match number of columns (${props.columns.length})`)
    super(props)
    if (!this.current_url) this.current_url = props.initial_url
    if (props.new_entry_row?.length)
      this.state.new_row = this.new_row_template
  }

  get new_row_template() {
    return {id: -1, url: "", ...this.props.new_row_values}
  }

  componentDidMount() {
    this.get_data(this.props.initial_url)
    console.log("Mounted AsyncTable", this)
  }

  componentDidUpdate(prevProps: AsyncTableProps) {
    console.log("Updated AsyncTable", this, prevProps)
    // Typical usage (don't forget to compare props):
    if (this.props.initial_url !== prevProps.initial_url)
      this.setState({row_data: []})
    if (this.props.initial_url !== prevProps.initial_url || this.props.last_updated !== prevProps.last_updated)
      this.get_data(this.props.initial_url)
  }

  reset_new_row = () => this.setState({new_row: this.props.new_row_values? this.new_row_template : null})

  get_data: (url: string) => void = async (url) => {
    this.setState({loading: true})
    if (!url) return;
    this.current_url = url;
    await Connection.fetch(url)
      .then(res => APIConnection.get_result_array(res))
      .then((res) => {
        console.log(res)
        this.setState({
          row_data: res.map(r => ({...r, _changed: false})),
          loading: false,
          loading_rows: []
        })
      })
      .catch(e => {
        console.error('Async Table error', e)
        this.setState({loading: false, loading_rows: []})
      })
  }

  refresh_row = async (row: {id: number, url: string, [key: string]: any}) => {
    const loading_rows = this.state.loading_rows.filter(i => i !== row.id)
    loading_rows.push(row.id)
    this.setState({loading_rows: loading_rows})
    await Connection.fetch(row.url)
      .then((res: SingleAPIResponse) => {
        // If we deleted the row, delete it in state
        if (res === 404)
          this.setState({row_data: this.state.row_data.filter(r => r.id !== row.id)})
        // otherwise, update
        else
          this.setState({row_data: this.state.row_data.map(r => r.id === row.id ? {...res, _changed: false} : r)})
      })
      .catch(e => console.error('AsyncTable.update_single_row error', e, row))
      .finally(
        () => this.setState({loading_rows: this.state.loading_rows.filter(i => i !== row.id)})
      )
  }

  update_all = async () => {
    this.reset_new_row()
    return this.get_data(this.current_url)
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

  row_conversion_context = (row: any, i: number) => ({
    column: this.props.columns[i],
    update: (event: BaseSyntheticEvent) => this.setState({
      // Amend row_data to include new value for [name]
      row_data: this.state.row_data.map(
        r => r.id === row.id ?
          {...row, [event.target.name]: event.target.value, _changed: true} : r
      )
    }),
    refresh: () => this.refresh_row(row),
    refresh_all_rows: this.update_all
  })

  wrap_cells_in_row = (contents: any, row_index: number) => {
    const cells = contents.map((cell: any, i: number) =>
      <TableCell {...this.props.columns[i].contentTableCellProps} key={`cell-${i}`}>{cell}</TableCell>
    )
    return <TableRow key={`row-${row_index}`}>{cells}</TableRow>
  }

  row_data_to_tablerow = (row: any, row_index: number) => {
    if (this.state.loading_rows.includes(row.id))
      return this.loading_row(row.id)

    const row_contents = this.props.rows.map((cell: any, i: number) => {
      if (typeof cell === 'function')
        return cell(row, this.row_conversion_context(row, i))
      return cell
    })
    return this.wrap_cells_in_row(row_contents, row_index)
  }

  new_row_to_tablerow = () => {
    if (!this.props.new_entry_row?.length)
      return <Fragment key="new_blank"/>
    const row_contents = this.props.new_entry_row.map((cell: any, i: number) => {
      if (typeof cell === 'function')
        return cell(this.state.new_row, {
          ...this.row_conversion_context(this.state.new_row, i),
          update: (event: BaseSyntheticEvent) => this.setState({
            new_row: {...this.state.new_row, [event.target.name]: event.target.value, _changed: true}
          })
        })
      return cell
    })
    return this.wrap_cells_in_row(row_contents, -1)
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
                this.props.new_entry_row?.length &&
                this.new_row_to_tablerow()
              }
            </TableBody>
          }
        </Table>
      </TableContainer>
    )
  }
}