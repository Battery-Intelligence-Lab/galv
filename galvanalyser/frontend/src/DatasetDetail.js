import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ResponsiveLine } from '@nivo/line'

export default function DatasetDetail() {
  let { data } = useParams();


  return (
    <ResponsiveLine
        data={data}
    />
  )
 
}
