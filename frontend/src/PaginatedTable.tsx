/**
 * Offer a table with previous/next links.
 */
import classNames from 'classnames'
import React, {Component, ReactComponentElement} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Button from '@mui/material/Button';
import Connection, {APIResponse, SingleAPIResponse} from "./APIConnection";
import TableRow from "@mui/material/TableRow";
import TableCell, {TableCellProps} from "@mui/material/TableCell";
import LoadingButton from "@mui/lab/LoadingButton";
import Tooltip, {TooltipProps} from "@mui/material/Tooltip";
import Typography, {TypographyProps} from "@mui/material/Typography";
import TableHead from "@mui/material/TableHead";

export type Heading = {
  label: string;
  help?: string;
  tableCellProps?: Partial<TableCellProps>;
  tooltipProps?: Partial<TooltipProps>;
  typographyProps?: Partial<TypographyProps>;
}

type CompleteHeading = {
  label: string;
  help: string;
  tableCellProps: Partial<TableCellProps>;
  tooltipProps: Partial<TooltipProps>;
  typographyProps: Partial<TypographyProps>;
}

export type RowFunProps<T> = {
  savedRow?: T;
  onRowSave: (row: any) => void;
  selected: boolean;
  onSelectRow: (id: any) => void;
  disabledSave?: boolean;
  addIcon?: boolean;
  [key: string]: any;
}

type RowFun = ((row: any, i: number, array: any[]) => ReactComponentElement<any>) |
  ((row: any, i: number) => ReactComponentElement<any>) |
  ((row: any) => ReactComponentElement<any>)

export type PaginatedTableProps = {
  column_headings: Heading[];
  row_fun: RowFun;
  initial_url: string;
  new_entry_row?: ReactComponentElement<any>;
  styles?: any;
  [key: string]: any;
}

type PaginatedTableState = {
  row_data: any[];
  links: PaginationLinks;
  last_updated: Date;
  loading: boolean;
  loading_rows: number[];
}

export type PaginationLinks = {
  previous?: string | null,
  next?: string | null,
}

type PaginationDataFun = (url?: string | null) => APIResponse

type PaginationProps = PaginationLinks & {
  get_data_fun: PaginationDataFun;
  position: string;
}


class Pagination extends Component<PaginationProps, {}> {
  render() {
    return (
      <div className={classNames({
        pagination: true,
        'pagination-above': this.props.position === 'above',
        'pagination-below': this.props.position === 'below',
      })}>
        <Button
          key="prev"
          disabled={!this.props.previous}
          onClick={(evt) => {
            evt.preventDefault();
            this.props.get_data_fun(this.props.previous)
          }}>
          Previous
        </Button>
        <Button
          key="next"
          disabled={!this.props.next}
          onClick={(evt) => {
            evt.preventDefault();
            this.props.get_data_fun(this.props.next)
          }}
        >
          Next
        </Button>
      </div>
    )
  }
}

export default class PaginatedTable extends Component<PaginatedTableProps, PaginatedTableState> {
  current_url: string = "";

  state: PaginatedTableState = {
    row_data: [],
    links: {previous: null, next: null},
    last_updated: new Date(0),
    loading: true,
    loading_rows: []
  }

  constructor(props: PaginatedTableProps) {
    super(props)
    if (!this.current_url) this.current_url = props.initial_url
  }

  componentDidMount() {
    this.get_data(this.props.initial_url)
    console.log("Mounted PaginatedTable", this)
  }

  componentDidUpdate(prevProps: PaginatedTableProps) {
    console.log("Updated PaginatedTable", this, prevProps)
    // Typical usage (don't forget to compare props):
    if (this.props.initial_url !== prevProps.initial_url)
      this.setState({row_data: []})
    if (this.props.initial_url !== prevProps.initial_url || this.props.last_updated !== prevProps.last_updated)
      this.get_data(this.props.initial_url)
  }

  get_data: PaginationDataFun = async (url) => {
    this.setState({loading: true})
    if (!url) return;
    this.current_url = url;
    await Connection.fetch(url)
      .then((res: APIResponse) => {
        console.log(res);
        this.setState({
          row_data: res.results,
          links: {
            next: res.next,
            previous: res.previous
          },
          loading: false,
          loading_rows: []
        })
      })
      .catch(e => {
        console.error('Paginated Table error', e)
        this.setState({loading: false, loading_rows: []})
      })
  }

  update_single_row = async (row: {id: number, [key: string]: any}) => {
    const loading_rows = this.state.loading_rows.filter(i => i !== row.id)
    loading_rows.push(row.id)
    this.setState({loading_rows: loading_rows})
    await Connection.fetch(row.url)
      .then((res: SingleAPIResponse) => {
        console.log(res)
        this.setState({row_data: this.state.row_data.map(r => r.id === row.id ? res : r)})
      })
      .catch(e => console.error('PaginatedTable.update_single_row error', e))
      .finally(
        () => this.setState({loading_rows: this.state.loading_rows.filter(i => i !== row.id)})
      )
  }

  get header_row() {
    const column_headings: CompleteHeading[] = this.props.column_headings.map(
      (heading: Heading) => ({
        label: heading.label,
        help: heading.help || "",
        tableCellProps: heading.tableCellProps || {},
        tooltipProps: heading.tooltipProps || {},
        typographyProps: heading.typographyProps || {},
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

  get loading_row() {
    return <TableRow key="loading">
      <TableCell colSpan={this.props.column_headings.length} align="center">
        <LoadingButton loading={true} />
      </TableCell>
    </TableRow>
  }

  render() {
    return (
      <div key="paginated-table" className="paginated-table">
        <Pagination
          key="top-pagination"
          position={'above'}
          previous={this.state.links.previous}
          next={this.state.links.next}
          get_data_fun={this.get_data}
        />
        <TableContainer key="paginated-table">
          <Table className={this.props.styles?.table} size="small">
            {this.header_row}
            {
              <TableBody key="body">
                {
                  this.state.loading && this.loading_row
                }
                {!this.state.loading && this.state.row_data.map(this.props.row_fun)}
                {!this.state.loading && this.props.new_entry_row}
              </TableBody>
            }
          </Table>
        </TableContainer>
        <Pagination
          key="bottom-pagination"
          position={'below'}
          previous={this.state.links.previous}
          next={this.state.links.next}
          get_data_fun={this.get_data}
        />
      </div>
    )
  }
}