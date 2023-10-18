import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {EquipmentFamiliesApi, EquipmentFamily, EquipmentApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps} from "../utils/misc";
import LoadingChip from "../utils/LoadingChip";
import QueryWrapper from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {PATHS} from "../../App";


export default function EquipmentFamilyChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

    const uuid = id_from_ref_props<string>(props)
    const api_handler = new EquipmentFamiliesApi()
    const query = useQuery<AxiosResponse<EquipmentFamily>, AxiosError>({
        queryKey: ['equipment_family_retrieve', uuid],
        queryFn: () => api_handler.equipmentFamiliesRetrieve(uuid)
    })

    return <QueryWrapper
        queries={[query]}
        loading={<LoadingChip url={`/equipment_families/${uuid}`} icon={<ICONS.FAMILY/>} {...props}/>}
        error={(queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS.EQUIPMENT_FAMILIES}/${uuid}`}
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
            label={`${query.data?.data.type} ${query.data?.data.manufacturer} ${query.data?.data.model}`}
            clickable={true}
            component={Link}
            to={`${PATHS.EQUIPMENT_FAMILIES}/${uuid}`}
            {...props as ChipProps as any}
        />}
    />

}