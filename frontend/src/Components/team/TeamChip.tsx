import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {TeamsApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import LoadingChip from "../LoadingChip";
import LabChip from "../lab/LabChip";

export default function TeamChip(props: ObjectReferenceProps & ChipProps) {
    const {classes} = useStyles();
    const team_id = id_from_ref_props<number>(props)
    const api_handler = new TeamsApi()
    const team_query = useQuery({
        queryKey: ['teams_retrieve', team_id],
        queryFn: () => api_handler.teamsRetrieve(team_id)
    })
    return team_query.isLoading ?
        <LoadingChip url={`/teams/${team_id}`} icon={<ICONS.TEAMS/>} {...props}/> :
        team_query.isError ? <LabChip {...props}/> : <Chip
            key={team_id}
            className={clsx(classes.item_chip, classes.team_chip)}
            icon={<ICONS.TEAMS/>}
            variant="outlined"
            label={team_query.isLoading ? '...' : team_query.data?.data.name}
            clickable={true}
            component={Link}
            to={`/teams/${team_id}`}
            {...props as ChipProps as any}
        />
}