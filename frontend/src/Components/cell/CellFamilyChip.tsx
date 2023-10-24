import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../../UseStyles";
import {CellFamiliesApi, CellFamily, CellsApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import {ICONS} from "../../icons";
import clsx from "clsx";
import {Link} from "react-router-dom";
import React from "react";
import {id_from_ref_props, ObjectReferenceProps, usePropParamId} from "../utils/misc";
import LoadingChip from "../utils/LoadingChip";
import QueryWrapper from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import ErrorChip from "../error/ErrorChip";
import {PATHS} from "../../App";


export default function CellFamilyChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

    const uuid = usePropParamId<string>(props)
    const api_handler = new CellFamiliesApi()
    const query = useQuery<AxiosResponse<CellFamily>, AxiosError>({
        queryKey: ['cell_family_retrieve', uuid],
        queryFn: () => api_handler.cellFamiliesRetrieve(uuid)
    })

    return <QueryWrapper
        queries={[query]}
        loading={<LoadingChip url={`/cell_families/${uuid}`} icon={<ICONS.FAMILY/>} {...props}/>}
        error={(queries) => <ErrorChip
            status={queries[0].error?.response?.status}
            target={`${PATHS.CELL_FAMILIES}/${uuid}`}
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
            label={`${query.data?.data.manufacturer} ${query.data?.data.model}: ${query.data?.data?.chemistry} ${query.data?.data?.form_factor} Cell`}
            clickable={true}
            component={Link}
            to={`${PATHS.CELL_FAMILIES}/${uuid}`}
            {...props as ChipProps as any}
        />}
    />

}