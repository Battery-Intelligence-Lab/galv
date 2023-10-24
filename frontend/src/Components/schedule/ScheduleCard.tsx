import {CardProps} from "@mui/material";
import {ExpandableCardProps, id_from_ref_props, usePropParamId} from "../utils/misc";
import {
    Schedule,
    ScheduleFamiliesApi,
    ScheduleFamily,
    SchedulesApi
} from "../../api_codegen";
import React from "react";
import ScheduleFamilyChip from "./ScheduleFamilyChip";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function ScheduleCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Schedule>, AddProps<ScheduleFamily>>
        target_uuid={uuid}
        target_type="schedules"
        target_api={SchedulesApi}
        family_api={ScheduleFamiliesApi}
        FamilyChip={ScheduleFamilyChip}
        path_key="SCHEDULES"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}