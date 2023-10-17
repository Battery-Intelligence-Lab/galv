import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {ScheduleFamiliesApi, ScheduleFamily, SchedulesApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import LoadingChip from "../LoadingChip";
import QueryWrapper from "../QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {PATHS} from "../../App";


export default function ScheduleFamilyChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

    const uuid = id_from_ref_props<string>(props)
    const api_handler = new ScheduleFamiliesApi()
    const query = useQuery<AxiosResponse<ScheduleFamily>, AxiosError>({
        queryKey: ['schedule_family_retrieve', uuid],
        queryFn: () => api_handler.scheduleFamiliesRetrieve(uuid)
    })

    return <QueryWrapper
        queries={[query]}
        loading={<LoadingChip url={`/schedule_families/${uuid}`} icon={<ICONS.FAMILY/>} {...props}/>}
        error={(queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS.SCHEDULE_FAMILIES}/${uuid}`}
            detail={queries[0].error?.response?.data?.toString()}
            key={uuid}
            icon={<ICONS.FAMILY />}
            variant="outlined"
            />
        }
        success={<Chip
            key={uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.FAMILY />}
            variant="outlined"
            label={query.data?.data.identifier}
            clickable={true}
            component={Link}
            to={`${PATHS.SCHEDULE_FAMILIES}/${uuid}`}
            {...props as ChipProps as any}
        />}
    />

}