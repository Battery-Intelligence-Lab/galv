import {CardProps} from "@mui/material";
import {ExpandableCardProps, usePropParamId} from "../utils/misc";
import {
    Schedule,
    ScheduleFamily,
} from "../../api_codegen";
import React from "react";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function ScheduleCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Schedule>>
        resource_id={uuid}
        lookup_key="SCHEDULE"
        editing={false}
        expanded={false}
        {...props}
    />
}