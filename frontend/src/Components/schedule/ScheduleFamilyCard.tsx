import {CardProps} from "@mui/material";
import { ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {
    ScheduleFamiliesApi,
    ScheduleFamily,
} from "../../api_codegen";
import React from "react";
import {AddProps} from "../utils/ChildCard";
import FamilyCard from "../utils/FamilyCard";

export default function ScheduleFamilyCard(props: Partial<ObjectReferenceProps> & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <FamilyCard<AddProps<ScheduleFamily>>
        family_id={uuid}
        lookup_key="SCHEDULE_FAMILY"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "schedules", "in_use", "team", "permissions"]}
        {...props}
    />
}