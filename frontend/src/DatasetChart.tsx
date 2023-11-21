// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {useState} from "react";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";
import CardHeader from "@mui/material/CardHeader";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import {ColumnsApi} from "./api_codegen";
import {useQueries, useQuery} from "@tanstack/react-query";
import useStyles from "./styles/UseStyles";
import clsx from "clsx";
import Box from "@mui/material/Box";
import Skeleton from "@mui/material/Skeleton";
import CanvasJSReact from "@canvasjs/react-charts";

const CanvasJSChart = CanvasJSReact.CanvasJSChart;

const COL_KEYS = ["Time", "Amps", "Volts"]

const KEY_COL_NAMES = {
    [COL_KEYS[0]]: "Time",
    [COL_KEYS[1]]: "Current",
    [COL_KEYS[2]]: "Potential difference"
}

const COLORS = {
    [COL_KEYS[1]]: "#de6565",
    [COL_KEYS[2]]: "#5d5dab"
}

/**
 * TODO: handle incoming data stream and render in response to new data chunks
 */
export function DatasetChart({file_uuid}: {file_uuid: string}) {
    const {classes} = useStyles()
    const maxDataPoints = 10000
    const [chartKey, setChartKey] = useState<number[]>([])

    const api_handler = new ColumnsApi()
    const columns_query = useQuery({
        queryKey: ["COLUMNS", file_uuid, "list"],
        queryFn: () => api_handler.columnsList(
            undefined,
            file_uuid,
            undefined,
            undefined,
            undefined,
            true
        )
    })
    const value_queries = useQueries({
        queries: (columns_query.data?.data.results ?? []).map((col) => ({
            queryKey: ["COLUMNS", file_uuid, col.id, "values"],
            queryFn: () => api_handler.columnsValuesRetrieve(col.id, {params: {max: maxDataPoints}})
        }))
    })

    const time_column = columns_query.data?.data.results?.findIndex((col) => col.type_name === "Time")

    const stream_to_numbers = (stream: any): (number|null)[] => {
        if (typeof stream !== "string") return []
        try {
            const lines = (stream as string).split("\n")
            const out = lines.map((line) => {
                try {
                    const n = Number(line)
                    if (!isNaN(n)) return n
                } catch {}
                return null
            })
            out.pop()   // Remove last element, which is always empty
            return out
        } catch (e) {
            console.error(`Error parsing stream to numbers`, {stream, e})
        }
        return []
    }

    const cols = columns_query.data?.data.results?.map((col) => col.type_name)

    const chart_data = value_queries
        .filter((_, i) => i !== time_column)
        .map((query, i) => {
            if (!query.data?.data || time_column === undefined) return {
                id: `Col ${i}`,
                data: []
            }
            if (!chartKey.includes(i)) setChartKey(prevState => [...prevState, i])
            const values = stream_to_numbers(query.data?.data)
            return {
                type: "line",
                name: KEY_COL_NAMES[cols?.[i] ?? ""] ?? `Col ${i}`,
                showInLegend: true,
                xValueFormatString: "#,##0.0000 s",
                yValueFormatString: `#,##0.0000 ${cols?.[i] ?? ""}`,
                axisYType: cols?.[i] === COL_KEYS[2]? "secondary" : "primary",
                color: COLORS[cols?.[i] ?? ""],
                dataPoints: stream_to_numbers(value_queries[time_column]?.data?.data).map((t, n) => {
                    return {
                        x: t,
                        y: values[n] ?? null
                    }
                })
            }
        }, {})

    return <CardContent>
        <Stack spacing={1}>
            <Box className={clsx(classes.chart)}>
                {
                    value_queries.some(q => q.isLoading) ||
                    columns_query.isLoading?
                        <Skeleton variant="rounded" height="300px"/> :
                        <CanvasJSChart
                            key={chartKey.reduce((a, b) => a + b, 0)}
                            options={{
                                theme: "light2",
                                animationEnabled: true,
                                title:{
                                    text: "Cycler data summary"
                                },
                                axisX: {
                                    title: "Time (s)",
                                },
                                axisY: {
                                    title: "Current (A)",
                                    titleFontColor: COLORS[COL_KEYS[1]],
                                    lineColor: COLORS[COL_KEYS[1]],
                                    labelFontColor: COLORS[COL_KEYS[1]],
                                    tickColor: COLORS[COL_KEYS[1]]
                                },
                                axisY2: {
                                    title: "Potential Difference (V)",
                                    titleFontColor: COLORS[COL_KEYS[2]],
                                    lineColor: COLORS[COL_KEYS[2]],
                                    labelFontColor: COLORS[COL_KEYS[2]],
                                    tickColor: COLORS[COL_KEYS[2]]
                                },
                                toolTip: {
                                    shared: true
                                },
                                data: chart_data
                            }}
                        />}
            </Box>
        </Stack>
    </CardContent>
}

export default function DatasetChartWrapper({file_uuid}: {file_uuid: string}) {
    const [open, setOpen] = useState<boolean>(false)

    return <Card>
        <CardHeader
            title={<Typography variant="h5">Dataset Chart</Typography>}
            subheader={<Typography variant="body1">View a chart of a dataset</Typography>}
            onClick={() => setOpen(!open)}
            sx={{cursor: "pointer"}}
        />
        {open && <DatasetChart file_uuid={file_uuid} />}
    </Card>
}