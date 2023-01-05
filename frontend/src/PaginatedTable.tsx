/**
 * Offer a table with previous/next links.
 */
import classNames from 'classnames'
import {TableHead, TableRow} from "@mui/material";
import {Component} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Connection, {APIResponse} from "./APIConnection";

type RowFunOptions = {
  savedRow: any,
  onRowSave: (row: any) => void,
  selected: boolean,
  onSelectRow: (id: number) => void,
  disabledSave: boolean,
  addIcon?: boolean,
  [key: string]: any
}

type RowFun = (row: any) => (options: RowFunOptions) => typeof TableRow

export type PaginationLinks = {
  previous?: string | null,
  next?: string | null,
}

type PaginationDataFun = (url?: string | null) => APIResponse

type PaginationProps = PaginationLinks & { get_data_fun: PaginationDataFun; position: string }


class Pagination extends Component<PaginationProps, {}> {
  render() {
    return (
    <div className={classNames({
      pagination: true,
      'pagination-above': this.props.position === 'above',
      'pagination-below': this.props.position === 'below',
    })}>
      <button
        disabled={!this.props.previous}
        onClick={(evt) => {
          evt.preventDefault();
          this.props.get_data_fun(this.props.previous)
        }}>
        Previous
      </button>
      <button
        disabled={!this.props.next}
        onClick={(evt) => {
          evt.preventDefault();
          this.props.get_data_fun(this.props.next)
        }}
      >
        Next
      </button>
    </div>
    )
  }
}

export type PaginatedTableProps = {
  header: typeof TableHead,
  row_fun: RowFun,
  initial_url: string,
  new_entry_row?: typeof TableRow,
  styles?: any,
  [key: string]: any
}

type PaginatedTableState = {
  row_data: any[],
  links: PaginationLinks
}

export default class PaginatedTable extends Component<PaginatedTableProps, PaginatedTableState> {
  header: typeof TableHead;
  row_fun: RowFun;
  new_entry_row: typeof TableRow | undefined;
  styles: any;
  initial_url: string;

  state = {
    row_data: [],
    links: {previous: null, next: null}
  }

  constructor(props: PaginatedTableProps) {
    super(props)
    this.header = props.data.header
    this.row_fun = props.data.row_fun
    this.new_entry_row = props.data.new_entry_row
    this.styles = props.data.styles
    this.initial_url = props.data.initial_url
  }

  componentDidMount() {
    this.get_data(this.initial_url)
  }

  get_data: PaginationDataFun = async (url) => {
    if (!url) return;
    await Connection.fetch(url)
      // @ts-ignore
      .then((res: APIResponse) => {
        console.log(res);
        this.setState({
          row_data: res.results,
          links: {
            next: res.next,
            previous: res.previous
          },
        })
      })
      .catch(e => {
        console.error('Paginated Table error', e)
      })
  }

  render() {
    return (
      <div className="paginated-table">
        <Pagination
          position={'above'}
          previous={this.state.links.previous}
          next={this.state.links.next}
          get_data_fun={this.get_data}
        />
        <TableContainer>
          {
            // @ts-ignore
            <Table className={this.styles.table} size="small">
              {this.header}
              {
                // @ts-ignore
                <TableBody>
                  {this.state.row_data.map(this.row_fun)}
                  {this.new_entry_row}
                </TableBody>
              }
            </Table>
          }
        </TableContainer>
        <Pagination
          position={'below'}
          previous={this.state.links.previous}
          next={this.state.links.next}
          get_data_fun={this.get_data}
        />
      </div>
    )
  }
}