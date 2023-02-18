import React, { useEffect, useState, Fragment } from "react";
import { ResponsiveLine, Datum } from '@nivo/line'
import {DatasetFields} from "./Datasets";
import Connection from "./APIConnection";
import CircularProgress from "@mui/material/CircularProgress";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import Stack from "@mui/material/Stack";

export type UnitFields = {
  name: string;
  symbol: string;
  description: string;
}

export type ColumnFields = {
  id: number;
  url: string;
  name: string;
  dataset: string;
  is_numeric: boolean;
  type_name: string;
  description: string;
  unit: UnitFields;
  data: string;
  data_list: string;
}

export type DatasetChartProps = {
  dataset: DatasetFields
}

export type ColumnDataFields<T extends string | number> = {
  id: number;
  url: string;
  observations: T[];
}

type keyColumnMap = {
  [column_name in "time" | "volts" | "amps"]: ColumnFields | undefined;
};

// These values come from the fixtures injected into Galvanalyser's backend
const TEST_TIME_COLUMN = "Time"
const VOLTAGE_COLUMN = "Volts"
const AMPS_COLUMN = "Amps"


export default function DatasetChart(props: DatasetChartProps) {
  const [columns, setColumns] = useState<ColumnFields[]>([])
  const [keyColumns, setKeyColumns] =
    useState<keyColumnMap>({time: undefined, amps: undefined, volts: undefined})
  const [timeseries, setTimeseries] = useState<{[id: number]: number[]}>({})
  const [loadingColumnData, setLoadingColumnData] = useState<number[]>([])
  const [textHeader, setTextHeader] = useState<JSX.Element>()
  let renderChart = false;

  useEffect(() => {
    Promise.all(props.dataset.columns.map(c => Connection.fetch<ColumnFields>(c)))
      .then(columns => {
        const cols = columns
          .map(c => c.content)
          .filter(c => c.is_numeric)
          .sort((arg1, arg2) => {
            const priority_cols = [VOLTAGE_COLUMN, AMPS_COLUMN]
            const args = [arg1, arg2].map(a => priority_cols.includes(a.type_name)? a.id + 1000 : a.id)

            return args[1] - args[0]
          })
        const time = cols.find(c => c.type_name === TEST_TIME_COLUMN)
        const volts = cols.find(c => c.type_name === VOLTAGE_COLUMN)
        const amps = cols.find(c => c.type_name === AMPS_COLUMN)
        setColumns(cols)
        setKeyColumns({time, volts, amps})
        if (time)
          fetchColumnData(time)
        if (volts)
          fetchColumnData(volts)
            .then(() => setSelectedColumns(prevState => [...prevState.filter(c => c.id !== volts.id), volts]))
        if (amps)
          fetchColumnData(amps)
            .then(() => setSelectedColumns(prevState => [...prevState.filter(c => c.id !== amps.id), amps]))
      })
      .then(() => {
      })
  }, [props.dataset])

  useEffect(() => {
    if (loadingColumnData.length)
      setTextHeader(<Fragment>
        <CircularProgress/>
        <Typography>
          {`Loading column data for ${loadingColumnData.length} columns...`}
        </Typography>
      </Fragment>)
    else if (!renderChart)
      setTextHeader(<CircularProgress/>)
    else
      setTextHeader(<Typography>Click a column in the legend to add its data to the graph</Typography>)
  }, [loadingColumnData, renderChart])

  const [selectedColumns, setSelectedColumns] = useState<ColumnFields[]>([])

  const fetchColumnData = (col: ColumnFields) => {
    setLoadingColumnData(prevState => [...prevState.filter(i => i !== col.id), col.id])
    return Connection.fetch<ColumnDataFields<number>>(col.data_list)
      .then(r => {console.log(r); return r})
      .then(response => response.content)
      .then(data => {
          setTimeseries(prevState => ({...prevState, [col.id]: data.observations}))
          setLoadingColumnData(prevState => prevState.filter(i => i !== col.id))
        }
      )
  }

  const handleLegendClick = (datum: Datum) => {
    const col = columns.find(c => get_series_name(c) === datum.id)
    if (!col) {
      return;
    }
    if (!(col.id in timeseries)) {
      fetchColumnData(col)
        .then(() => setSelectedColumns(prevState => [...prevState, col]))
    } else {
      if (selectedColumns.map(c => c.id).includes(col.id))
        setSelectedColumns(prevState => prevState.filter(c => c.id !== col.id))
      else
        setSelectedColumns(prevState => [...prevState, col])
    }
  };

  const get_series_name = (col: ColumnFields) => `${col.name} [${col.id}]`

  const chart_data = columns.filter(c => c.id !== keyColumns.time?.id).map((col: ColumnFields) => {
    const defaultData = {
      id: get_series_name(col),
      data: [{
        x: 0,
        y: 0,
      }]
    };
    if (keyColumns.time === undefined || !timeseries[keyColumns.time.id]) {
      return defaultData;
    }
    if (!timeseries[col.id]) {
      return defaultData;
    }
    if (!selectedColumns.map(c => c.id).includes(col.id)) {
      return defaultData;
    }
    renderChart = true;
    let data = []
    let subsample = timeseries[col.id].length / 1000.0;
    if (subsample < 1) {
      subsample = 1.0;
    }
    const int_subsample = Math.round(subsample);
    for(let i = 0; i < timeseries[col.id].length; i += int_subsample) {
      data.push({
        x: timeseries[keyColumns.time.id][i],
        y: timeseries[col.id][i],
      });
    }
    return {
      id: get_series_name(col),
      data: data,
    };
  })

  return (
    <Grid
      sx={{ height: 300, width: '100%' }}
      container
      direction="row"
      justifyContent="center"
      alignItems="center"
    >
      <Grid item>
        <Stack
          spacing={4}
          direction="row"
          alignItems="center"
        >
          {textHeader}
        </Stack>
      </Grid>
      {renderChart &&
          <Grid item sx={{height: '100%', width: '100%'}}>
              <ResponsiveLine
                  data={chart_data}
                  margin={{ top: 50, right: 160, bottom: 50, left: 60 }}
                  enablePoints={false}
                  xScale={{ type: 'linear' }}
                  yScale={{ type: 'linear', min: 'auto', max: 'auto'}}
                  axisLeft={{
                    legend: 'measurement',
                    legendOffset: -40,
                    legendPosition: 'middle'
                  }}
                  axisBottom={{
                    tickSize: 5,
                    tickPadding: 5,
                    tickRotation: 0,
                    format: '.2f',
                    legend: 'time',
                    legendOffset: 36,
                    legendPosition: 'middle'
                  }}
                  colors={{ scheme: 'category10' }}
                  lineWidth={2}
                  legends={[
                    {
                      anchor: 'bottom-right',
                      direction: 'column',
                      justify: false,
                      translateX: 140,
                      translateY: 0,
                      itemsSpacing: 2,
                      itemDirection: 'left-to-right',
                      itemWidth: 80,
                      itemHeight: 12,
                      itemOpacity: 0.75,
                      symbolSize: 12,
                      symbolShape: 'circle',
                      symbolBorderColor: 'rgba(0, 0, 0, .5)',
                      effects: [
                        {
                          on: 'hover',
                          style: {
                            itemBackground: 'rgba(0, 0, 0, .03)',
                            itemOpacity: 1
                          }
                        }
                      ],
                      onClick: handleLegendClick,
                    }
                  ]}

              />
          </Grid>
      }
    </Grid>
  )

}
