import React, { useEffect, useState } from "react";
import { ResponsiveLine } from '@nivo/line'
import { timeseries_column, columns } from './Api'

const TEST_TIME_COLUMN_ID = 1
const VOLTAGE_COLUMN_ID = 2
const AMPS_COLUMN_ID = 3


export default function DatasetDetail(props) {
  const { dataset } = props;

  const [timeseries, setTimeseries] = useState({})
  const [cols, setCols] = useState([])
  const [selectedColumns, setSelectedColumns] = useState([
    TEST_TIME_COLUMN_ID, VOLTAGE_COLUMN_ID, AMPS_COLUMN_ID
  ])

  useEffect(() => {
    columns(dataset.id).then((response) => {
      if (response.ok) {
        return response.json().then(setCols);
      }
    });
  }, [dataset.id])

  useEffect(() => {
    let new_columns = {}
    for (let i=0; i<selectedColumns.length; i++) {
      if (!timeseries[selectedColumns[i]]) {
        timeseries_column(dataset.id, selectedColumns[i]).then(
          (array) => {
            const key = selectedColumns[i];
            timeseries[key] = array;
            setTimeseries(
              timeseries 
            );
          }
        );
      }
    }
  }, [dataset.id]);

  const chart_data = selectedColumns.map((col_id) => {
    const col = cols.filter((col) => {
      return col_id === col.id;
    })[0];
    if (!col) {
      return {}
    }
    if (!timeseries[col.id]) {
      console.log('no timeseries', col.id, timeseries)
      return {}
    }
    if (!timeseries[TEST_TIME_COLUMN_ID]) {
      console.log('no time timeseries', col.id, timeseries)
      return {}
    }
    console.log(timeseries[col.id])
    return {
      id: col.name,
      data: timeseries[col.id].map((v, i) => {
        return {
          x: timeseries[TEST_TIME_COLUMN_ID][i],
          y: v,
        };
      })
    };
  });
  console.log(chart_data[0]);

  return (
    <ResponsiveLine
        data={chart_data}
    />
  )
 
}
