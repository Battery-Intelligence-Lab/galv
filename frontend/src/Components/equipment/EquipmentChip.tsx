import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {EquipmentApi, EquipmentFamiliesApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import LoadingChip from "../LoadingChip";

export default function EquipmentChip(props: ObjectReferenceProps & ChipProps) {
    const {classes} = useStyles();
    const equipment_uuid = id_from_ref_props<string>(props)
    const api_handler = new EquipmentApi()
    const family_api_handler = new EquipmentFamiliesApi()
    const equipment_query = useQuery({
        queryKey: ['equipment_retrieve', equipment_uuid],
        queryFn: () => api_handler.equipmentRetrieve(equipment_uuid)
    })
    const family_query = useQuery({
        queryKey: ['equipment_family_retrieve', equipment_query.data?.data.family],
        queryFn: () => family_api_handler.equipmentFamiliesRetrieve(id_from_ref_props<string>(equipment_query.data!.data.family)),
        enabled: !!equipment_query.data?.data.family
    })
    return equipment_query.isLoading ?
        <LoadingChip url={`/equipment/${equipment_uuid}`} icon={<ICONS.EQUIPMENT/>} {...props}/> :
        <Chip
            key={equipment_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.EQUIPMENT/>}
            variant="outlined"
            label={
                equipment_query.isLoading || family_query.isLoading ? '...' :
                    `${family_query.data?.data.type}: ${family_query.data?.data.manufacturer} ${family_query.data?.data.model}`
            }
            clickable={true}
            component={Link}
            to={`/equipment/${equipment_uuid}`}
            {...props as ChipProps as any}
        />
}