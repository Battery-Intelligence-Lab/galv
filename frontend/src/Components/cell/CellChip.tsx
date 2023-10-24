import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {CellFamiliesApi, CellsApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps, usePropParamId} from "../utils/misc";
import LoadingChip from "../utils/LoadingChip";


export default function CellChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

    const cell_uuid = usePropParamId<string>(props)
    const api_handler = new CellsApi()
    const family_api_handler = new CellFamiliesApi()
    const cell_query = useQuery({
        queryKey: ['cell_retrieve', cell_uuid],
        queryFn: () => api_handler.cellsRetrieve(cell_uuid)
    })
    const family_query = useQuery({
        queryKey: ['cell_family_retrieve', cell_query.data?.data.family],
        queryFn: () => family_api_handler.cellFamiliesRetrieve(id_from_ref_props<string>(cell_query.data!.data.family)),
        enabled: !!cell_query.data?.data.family
    })

    return cell_query.isLoading?
        <LoadingChip url={`/cells/${cell_uuid}`} icon={<ICONS.CELLS/>} {...props}/> :
        <Chip
            key={cell_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.CELLS />}
            variant="outlined"
            label={
                family_query.isLoading? '...' :
                    `${family_query.data?.data.manufacturer} ${family_query.data?.data.model} ${cell_query.data?.data?.identifier}`
            }
            clickable={true}
            component={Link}
            to={`/cells/${cell_uuid}`}
            {...props as ChipProps as any}
        />
}