import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {ScheduleFamiliesApi, SchedulesApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import LoadingChip from "../LoadingChip";

export default function ScheduleChip(props: ObjectReferenceProps & ChipProps) {
    const {classes} = useStyles();

    const schedule_uuid = id_from_ref_props<string>(props)
    const api_handler = new SchedulesApi()
    const family_api_handler = new ScheduleFamiliesApi()
    const schedule_query = useQuery({
        queryKey: ['schedule_retrieve', schedule_uuid],
        queryFn: () => api_handler.schedulesRetrieve(schedule_uuid)
    })
    const family_query = useQuery({
        queryKey: ['schedule_family_retrieve', schedule_query.data?.data.family],
        queryFn: () => family_api_handler.scheduleFamiliesRetrieve(id_from_ref_props<string>(schedule_query.data!.data.family)),
        enabled: !!schedule_query.data?.data.family
    })

    return schedule_query.isLoading ?
        <LoadingChip url={`/schedules/${schedule_uuid}`} icon={<ICONS.SCHEDULES/>} {...props}/> :
        <Chip
            key={schedule_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.SCHEDULES/>}
            variant="outlined"
            label={family_query.isLoading ? '...' : family_query.data?.data.identifier}
            clickable={true}
            component={Link}
            to={`/schedules/${schedule_uuid}`}
            {...props as ChipProps as any}
        />
}