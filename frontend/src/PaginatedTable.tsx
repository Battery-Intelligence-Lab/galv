/**
 * Offer a table with previous/next links.
 */
import classNames from 'classnames'
import {Component, ReactComponentElement} from "react";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import Button from '@mui/material/Button';
import Connection, {APIResponse} from "./APIConnection";

export type RowFunProps<T> = {
  savedRow?: T;
  onRowSave: (row: any) => void;
  selected: boolean;
  onSelectRow: (id: any) => void;
  disabledSave?: boolean;
  addIcon?: boolean;
  [key: string]: any;
}

type RowFun = (row: any) => ReactComponentElement<any>

export type PaginatedTableProps = {
  header: ReactComponentElement<any>,
  row_fun: RowFun,
  initial_url: string,
  new_entry_row?: ReactComponentElement<any>,
  styles?: any,
  [key: string]: any
}

type PaginatedTableState = {
  row_data: any[];
  links: PaginationLinks;
  last_updated: Date;
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
        disabled={!this.props.previous}
        onClick={(evt) => {
          evt.preventDefault();
          this.props.get_data_fun(this.props.previous)
        }}>
        Previous
      </Button>
      <Button
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

  state = {
    row_data: [],
    links: {previous: null, next: null},
    last_updated: new Date(0)
  }

  constructor(props: PaginatedTableProps) {
    super(props)
    if (!this.current_url) this.current_url = props.initial_url
  }

  componentDidMount() {
    this.get_data(this.props.initial_url)
  }

  componentDidUpdate(prevProps: PaginatedTableProps) {
    // Typical usage (don't forget to compare props):
    if (this.props.last_updated !== prevProps.last_updated) {
      this.get_data(this.props.initial_url);
    }
  }

  get_data: PaginationDataFun = async (url) => {
    if (!url) return;
    this.current_url = url;
    await Connection.fetch(url)
      // @ts-ignore
      .then((res: APIResponse) => {
        console.log(res);
        this.setState({
          row_data: res.results,
          links: {
            next: res.next,
            previous: res.previous
          }
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
            <Table className={this.props.styles.table} size="small">
              {this.props.header}
              {
                // @ts-ignore
                <TableBody>
                  {this.state.row_data.map(this.props.row_fun)}
                  {this.props.new_entry_row}
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