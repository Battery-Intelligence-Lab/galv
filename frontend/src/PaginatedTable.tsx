// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

export type unused = any
// /**
//  * Offer a table with previous/next links.
//  */
// import classNames from 'classnames'
// import React, {Component, ReactComponentElement} from "react";
// import TableContainer from "@mui/material/TableContainer";
// import Table from "@mui/material/Table";
// import TableBody from "@mui/material/TableBody";
// import Button from '@mui/material/Button';
// import Connection, {APIResponse, APIObject, SingleAPIResponse} from "./APIConnection";
// import TableRow from "@mui/material/TableRow";
// import TableCell, {TableCellProps} from "@mui/material/TableCell";
// import LoadingButton from "@mui/lab/LoadingButton";
// import Tooltip, {TooltipProps} from "@mui/material/Tooltip";
// import Typography, {TypographyProps} from "@mui/material/Typography";
// import TableHead from "@mui/material/TableHead";
// import AsyncTable from "./AsyncTable";
//
// type PaginatedTableProps = {
//   initial_url: string;
// }
//
// type PaginatedTableState = {
//   links: PaginationLinks;
//   current_url: string;
// }
//
// export type PaginationLinks = {
//   previous?: string | null,
//   next?: string | null,
// }
//
// type PaginationDataFun = (url?: string | null) => APIResponse
//
// type PaginationProps = PaginationLinks & {
//   get_data_fun: PaginationDataFun;
//   position: string;
// }
//
//
// class Pagination<T extends SingleAPIResponse> extends AsyncTable<T><PaginationProps, {}> {
//   render() {
//     return (
//       <div className={classNames({
//         pagination: true,
//         'pagination-above': this.props.position === 'above',
//         'pagination-below': this.props.position === 'below',
//       })}>
//         <Button
//           key="prev"
//           disabled={!this.props.previous}
//           onClick={(evt) => {
//             evt.preventDefault();
//             this.props.get_data_fun(this.props.previous)
//           }}>
//           Previous
//         </Button>
//         <Button
//           key="next"
//           disabled={!this.props.next}
//           onClick={(evt) => {
//             evt.preventDefault();
//             this.props.get_data_fun(this.props.next)
//           }}
//         >
//           Next
//         </Button>
//       </div>
//     )
//   }
// }
//
// export default class PaginatedTable<T extends SingleAPIResponse> extends Component<PaginatedTableProps, PaginatedTableState> {
//
//   state: PaginatedTableState = {
//     links: {previous: null, next: null},
//     current_url: ""
//   }
//
//   constructor(props: PaginatedTableProps) {
//     super(props)
//     if (!this.state.current_url) this.state.current_url = props.initial_url
//   }
//
//   componentDidMount() {
//     this.get_data(this.props.initial_url)
//     console.log("Mounted PaginatedTable", this)
//   }
//
//   render() {
//     return (
//       <div key="paginated-table" className="paginated-table">
//         <Pagination
//           key="top-pagination"
//           position={'above'}
//           previous={this.state.links.previous}
//           next={this.state.links.next}
//           get_data_fun={this.get_data}
//         />
//         <AsyncTable columns={} row_generator={} initial_url={} />
//         <Pagination
//           key="bottom-pagination"
//           position={'below'}
//           previous={this.state.links.previous}
//           next={this.state.links.next}
//           get_data_fun={this.get_data}
//         />
//       </div>
//     )
//   }
// }