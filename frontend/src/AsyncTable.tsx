import React, {Component, ReactElement, BaseSyntheticEvent, ReactEventHandler} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Connection, {APIConnection, APIObject} from "./APIConnection";
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

export type RowGeneratorContext<T> = {
  columns: Column[];
  update: ReactEventHandler;
  update_direct: <K extends keyof T>(field_name: K, new_value: T[K]) => void;
  refresh: () => void;
  refresh_all_rows: () => void;
  is_new_row: boolean;
  value_changed: boolean;
}

export type RowGenerator<T extends APIObject> =
  ((row_data: T) => ReactElement[]) |
  ((row_data: T, context: RowGeneratorContext<T>) => ReactElement[])

type CompleteHeading = {
  label: string;
  help: string;
  tableCellProps: Partial<TableCellProps>;
  tooltipProps: Partial<TooltipProps>;
  typographyProps: Partial<TypographyProps>;
}

export type AsyncTableProps<T extends APIObject> = {
  columns: Column[];
  row_generator: RowGenerator<T>;
  initial_url: string;
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
 */
export default class AsyncTable<T extends APIObject> extends Component<AsyncTableProps<T>, AsyncTableState> {
  current_url: string = "";

  state: AsyncTableState = {
    row_data: [],
    new_row: null,
    loading: true,
    loading_rows: [],
    changed_rows: []
  }

  constructor(props: AsyncTableProps<T>) {
    super(props)
    if (!this.current_url) this.current_url = props.initial_url
    if (props.new_row_values !== undefined)
      this.state.new_row = this.new_row_template
  }

  get new_row_template() {
    return {id: -1, url: "", ...this.props.new_row_values}
  }

  componentDidMount() {
    this.get_data(this.props.initial_url)
    console.log("Mounted AsyncTable", this)
  }

  componentDidUpdate(prevProps: AsyncTableProps<T>) {
    console.log("Updated AsyncTable", this, prevProps)
    // Typical usage (don't forget to compare props):
    if (this.props.initial_url !== prevProps.initial_url) {
      this.setState({row_data: []})
      this.get_data(this.props.initial_url)
    }
  }

  reset_new_row = () => this.setState({new_row: this.props.new_row_values? this.new_row_template : null})

  get_data: (url: string) => void = async (url) => {
    this.setState({loading: true})
    if (!url) return;
    this.current_url = url;
    await Connection.fetch(url)
      .then(APIConnection.get_result_array)
      .then((res) => {
        if (typeof(res) === 'number')
          throw new Error(res.toString())
        console.log(res)
        this.setState({
          row_data: res,
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

  refresh_row = async (row: {id: number, url: string, [key: string]: any}) => {
    const loading_rows = this.state.loading_rows.filter(i => i !== row.id)
    loading_rows.push(row.id)
    this.setState({loading_rows: loading_rows})
    await Connection.fetch(row.url)
      .then(APIConnection.get_result_array)
      .then((res) => {
        // If we deleted the row, delete it in state
        if (typeof res === 'number') {
          console.info(`${row.url} -> ${res}`)
          this.setState({row_data: this.state.row_data.filter(r => r.id !== row.id)})
        } else {
          // otherwise, update
          const row_data = res.pop()
          if (row_data === undefined) {
            console.error(res)
            throw new Error(`refresh_row expected 1 API result, got ${res.length}`)
          }
          this.setState({
            row_data: this.state.row_data.map(r => r.id === row.id ? row_data : r),
            changed_rows: this.state.changed_rows.filter(i => i !== row_data.id)
          })
        }
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

  row_conversion_context = (row: any, is_new_row: boolean) => {
    let update_fun: RowGeneratorContext<T>["update_direct"] = (name, value) => this.setState({
      // Amend row_data to include new value for [name]
      row_data: this.state.row_data.map(
        r => r.id === row.id ? {...row, [name]: value} : r
      ),
      changed_rows: [...this.state.changed_rows, row.id]
    })
    if (is_new_row)
      update_fun = (name, value) => this.setState({
        new_row: {...this.state.new_row, [name]: value, _changed: true},
        changed_rows: [...this.state.changed_rows, row.id]
      })

    return {
      columns: this.props.columns,
      update: (event: BaseSyntheticEvent) => update_fun(event.target.name, event.target.value),
      update_direct: update_fun,
      refresh: () => this.refresh_row(row),
      refresh_all_rows: this.update_all,
      is_new_row,
      value_changed: this.state.changed_rows.includes(row.id)
    }
  }

  wrap_cells_in_row = (contents: ReactElement[], row_index: number) => {
    const cells = contents.map((cell: any, i: number) =>
      <TableCell {...this.props.columns[i].contentTableCellProps} key={`cell-${i}`}>{cell}</TableCell>
    )
    return <TableRow key={`row-${row_index}`}>{cells}</TableRow>
  }

  row_data_to_tablerow = (row: T, row_index: number) => {
    const is_new_row = row_index === NEW_ROW_ID
    if (is_new_row)
      row_index = -1

    if (this.state.loading_rows.includes(row.id))
      return this.loading_row(row.id)

    const row_contents = this.props.row_generator(row, this.row_conversion_context(row, is_new_row))
    return this.wrap_cells_in_row(row_contents, row_index)
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