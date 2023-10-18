import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {LabsApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../utils/misc";
import LoadingChip from "../utils/LoadingChip";

export default function LabChip(props: ObjectReferenceProps & ChipProps) {
    const {classes} = useStyles();
    const lab_id = id_from_ref_props<number>(props)
    const api_handler = new LabsApi()
    const lab_query = useQuery({
        queryKey: ['labs_retrieve', lab_id],
        queryFn: () => api_handler.labsRetrieve(lab_id)
    })
    return lab_query.isLoading ? <LoadingChip url={`labs/${lab_id}`} icon={<ICONS.LABS/>}/> :
        <Chip
            key={lab_id}
            className={clsx(classes.item_chip, classes.team_chip)}
            icon={<ICONS.LABS/>}
            variant="outlined"
            label={lab_query.isLoading ? '...' : lab_query.data?.data.name}
            clickable={true}
            component={Link}
            to={`/labs/${lab_id}`}
            {...props as ChipProps as any}
        />
}