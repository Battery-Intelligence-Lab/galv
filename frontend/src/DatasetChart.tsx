// // SPDX-License-Identifier: BSD-2-Clause
// // Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// // of Oxford, and the 'Galv' Developers. All rights reserved.
//
// import React, { useEffect, useState, Fragment } from "react";
// import { ResponsiveLine, Datum } from '@nivo/line'
// import Connection from "./APIConnection";
// import CircularProgress from "@mui/material/CircularProgress";
// import Typography from "@mui/material/Typography";
// import Stack from "@mui/material/Stack";
// import Box from "@mui/material/Box";
// import TextField from "@mui/material/TextField";
//
// export type UnitFields = {
//   url: string;
//   id: number;
//   name: string;
//   symbol: string;
//   description: string;
// }
//
// export type ColumnFields = {
//   id: number;
//   url: string;
//   name: string;
//   dataset: string;
//   is_numeric: boolean;
//   type_name: string;
//   data_type: string;
//   description: string;
//   official_sample_counter: boolean;
//   unit: UnitFields;
//   values: string;
// }
//
// export type DatasetChartProps = any
//
// export type ColumnDataFields<T extends string | number> = {
//   id: number;
//   url: string;
//   observations: T[];
// }
//
// type keyColumnMap = {
//   [column_name in "time" | "volts" | "amps"]: ColumnFields | undefined;
// };
//
// // These values come from the fixtures injected into Galv's backend
// const TEST_TIME_COLUMN = "Time"
// const VOLTAGE_COLUMN = "Volts"
// const AMPS_COLUMN = "Amps"
//
// function Chart(props: DatasetChartProps & {filter: string}) {
//   const [columns, setColumns] = useState<ColumnFields[]>([])
//   const [keyColumns, setKeyColumns] =
//     useState<keyColumnMap>({time: undefined, amps: undefined, volts: undefined})
//   const [timeseries, setTimeseries] = useState<{[id: number]: number[]}>({})
//   const [loadingColumnData, setLoadingColumnData] = useState<number[]>([])
//   const [textHeader, setTextHeader] = useState<JSX.Element>()
//   let renderChart = false;
//
//   useEffect(() => {
//     Promise.all(props.dataset.columns.map(c => Connection.fetch<ColumnFields>(c)))
//       .then(columns => {
//         const cols = columns
//           .map(c => c.content)
//           .sort((arg1, arg2) => {
//             const priority_cols = [VOLTAGE_COLUMN, AMPS_COLUMN]
//             const args = [arg1, arg2].map(a => priority_cols.includes(a.type_name)? a.id + 1000 : a.id)
//
//             return args[1] - args[0]
//           })
//         const time = cols.find(c => c.type_name === TEST_TIME_COLUMN)
//         const volts = cols.find(c => c.type_name === VOLTAGE_COLUMN)
//         const amps = cols.find(c => c.type_name === AMPS_COLUMN)
//         setColumns(cols.filter(c => !c.official_sample_counter))
//         setKeyColumns({time, volts, amps})
//         if (time)
//           fetchColumnData(time)
//         if (volts)
//           fetchColumnData(volts)
//             .then(() => setSelectedColumns(prevState => [...prevState.filter(c => c.id !== volts.id), volts]))
//         if (amps)
//           fetchColumnData(amps)
//             .then(() => setSelectedColumns(prevState => [...prevState.filter(c => c.id !== amps.id), amps]))
//       })
//       .then(() => {
//       })
//   }, [props.dataset, props.filter])
//
//   useEffect(() => {
//     if (loadingColumnData.length)
//       setTextHeader(<Fragment>
//         <CircularProgress/>
//         <Typography>
//           {`Loading column data for ${loadingColumnData.length} columns...`}
//         </Typography>
//       </Fragment>)
//     else if (!renderChart)
//       setTextHeader(<CircularProgress/>)
//     else
//       setTextHeader(<Typography>Click a column in the legend to add its data to the graph</Typography>)
//   }, [loadingColumnData, renderChart])
//
//   const [selectedColumns, setSelectedColumns] = useState<ColumnFields[]>([])
//
//   const fetchColumnData = async (col: ColumnFields) => {
//     setLoadingColumnData(prevState => [...prevState.filter(i => i !== col.id), col.id])
//     const data: number[] = []
//     const response = await Connection.fetchRaw<ReadableStream>(`${col.values}?${props.filter}`, {});
//     const reader = response.getReader();
//     const decoder = new TextDecoder();
//     let _done = false;
//
//     while (!_done) {
//       const {done, value} = await reader.read();
//       _done = done;
//       if (done) break;
//       try {
//         const decoded = decoder.decode(value).split("\n").filter(s => s.length);
//         data.push(...decoded.map(d => Number(d)));
//         // console.log(`Parsed ${decoded.length} values from ${decoded}: ${decoded.map(d => Number(d))}`)
//       } catch (e) {
//         console.warn(`Failed to parse value '${value}'`)
//       }
//     }
//     setTimeseries(prevState => ({...prevState, [col.id]: data}))
//     setLoadingColumnData(prevState => prevState.filter(i => i !== col.id))
//   }
//
//   const handleLegendClick = (datum: Datum) => {
//     const col = columns.find(c => get_series_name(c) === datum.id)
//     if (!col) {
//       return;
//     }
//     if (!(col.id in timeseries)) {
//       fetchColumnData(col)
//         .then(() => setSelectedColumns(prevState => [...prevState, col]))
//     } else {
//       if (selectedColumns.map(c => c.id).includes(col.id))
//         setSelectedColumns(prevState => prevState.filter(c => c.id !== col.id))
//       else
//         setSelectedColumns(prevState => [...prevState, col])
//     }
//   };
//
//   const get_series_name = (col: ColumnFields) => `${col.name} [${col.id}]`
//
//   const chart_data = columns.filter(c => c.id !== keyColumns.time?.id).map((col: ColumnFields) => {
//     const defaultData = {
//       id: get_series_name(col),
//       data: [{
//         x: 0,
//         y: 0,
//       }]
//     };
//     if (keyColumns.time === undefined || !timeseries[keyColumns.time.id]) {
//       return defaultData;
//     }
//     if (!timeseries[col.id]) {
//       return defaultData;
//     }
//     if (!selectedColumns.map(c => c.id).includes(col.id)) {
//       return defaultData;
//     }
//     renderChart = true;
//     let data = []
//     let subsample = timeseries[col.id].length / 1000.0;
//     if (subsample < 1) {
//       subsample = 1.0;
//     }
//     const int_subsample = Math.round(subsample);
//     for(let i = 0; i < timeseries[col.id].length; i += int_subsample) {
//       data.push({
//         x: timeseries[keyColumns.time.id][i],
//         y: timeseries[col.id][i],
//       });
//     }
//     return {
//       id: get_series_name(col),
//       data: data,
//     };
//   })
//
//   return (
//     <Fragment>
//       <Stack
//         sx={{ width: '100%' }}
//         spacing={4}
//         direction="row"
//         alignItems="center"
//         justifyContent="center"
//       >
//         {textHeader}
//       </Stack>
//       <Box sx={{ height: 500, width: '95%' }}>
//         {renderChart &&
//             <ResponsiveLine
//                 data={chart_data}
//                 margin={{ top: 50, right: 160, bottom: 50, left: 60 }}
//                 enablePoints={false}
//                 xScale={{ type: 'linear' }}
//                 yScale={{ type: 'linear', min: 'auto', max: 'auto'}}
//                 axisLeft={{
//                   legend: 'measurement',
//                   legendOffset: -40,
//                   legendPosition: 'middle'
//                 }}
//                 axisBottom={{
//                   tickSize: 5,
//                   tickPadding: 5,
//                   tickRotation: 0,
//                   format: '.2f',
//                   legend: 'time',
//                   legendOffset: 36,
//                   legendPosition: 'middle'
//                 }}
//                 colors={{ scheme: 'category10' }}
//                 lineWidth={2}
//                 legends={[
//                   {
//                     anchor: 'bottom-right',
//                     direction: 'column',
//                     justify: false,
//                     translateX: 140,
//                     translateY: 0,
//                     itemsSpacing: 2,
//                     itemDirection: 'left-to-right',
//                     itemWidth: 80,
//                     itemHeight: 12,
//                     itemOpacity: 0.75,
//                     symbolSize: 12,
//                     symbolShape: 'circle',
//                     symbolBorderColor: 'rgba(0, 0, 0, .5)',
//                     effects: [
//                       {
//                         on: 'hover',
//                         style: {
//                           itemBackground: 'rgba(0, 0, 0, .03)',
//                           itemOpacity: 1
//                         }
//                       }
//                     ],
//                     onClick: handleLegendClick,
//                   }
//                 ]}
//             />
//         }
//       </Box>
//     </Fragment>
//   )
//
// }
//
// export default function DatasetChart(props: DatasetChartProps) {
//   const [filterMin, setFilterMin] = useState<number>(0)
//   const [filterMod, setFilterMod] = useState<number>(1)
//   const [filterMax, setFilterMax] = useState<number|undefined>(2000)
//   const [filter, setFilter] = useState<string>(get_filter_str())
//
//   function get_filter_str() {
//     const max = filterMax === undefined ? '' : `&max=${filterMax}`
//     const mod = filterMod === undefined ? '' : `&mod=${filterMod}`
//     return `min=${filterMin}${max}${mod}`
//   }
//
//   useEffect(
//     () => setFilter(get_filter_str()),
//     [filterMin, filterMax, filterMod]
//   )
//
//   return (
//     <Stack spacing={1} sx={{width: '100%'}} justifyContent="center" alignItems="center">
//       <Chart dataset={props.dataset} filter={filter}/>
//       <Stack
//         spacing={4}
//         direction="row"
//         alignItems="center"
//         justifyContent="center"
//       >
//         <TextField
//           name="filter_min"
//           label="Start at record"
//           type={"number"}
//           value={filterMin}
//           onChange={e => setFilterMin(parseInt(e.target.value))}
//         />
//         <TextField
//           name="filter_max"
//           label="End at record"
//           type={"number"}
//           value={filterMax}
//           onChange={e => {
//             const v = parseInt(e.target.value)
//             setFilterMax(v? v : undefined)
//           }}
//         />
//         <TextField
//           name="filter_mod"
//           label="Show every Nth record"
//           type={"number"}
//           value={filterMod}
//           onChange={e => setFilterMod(parseInt(e.target.value))}
//         />
//       </Stack>
//     </Stack>
//   )
//
// }
export {}