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

    return <ResourceCard<AddProps<Schedule>, AddProps<ScheduleFamily>>
        uuid={uuid}
        lookup_key="SCHEDULE"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}