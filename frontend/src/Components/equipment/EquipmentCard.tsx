import {CardProps} from "@mui/material";
import {id_from_ref_props, ObjectReferenceProps} from "../utils/misc";
import useStyles from "../../UseStyles";
import {Equipment, EquipmentFamiliesApi, EquipmentFamily, EquipmentApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import {Link} from "react-router-dom";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import clsx from "clsx";
import CardHeader from "@mui/material/CardHeader";
import CircularProgress from "@mui/material/CircularProgress";
import A from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import LoadingChip from "../utils/LoadingChip";
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import EquipmentFamilyChip from "./EquipmentFamilyChip";
import React from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import CountBadge from "../utils/CountBadge";
import {PATHS} from "../../App";

export default function EquipmentCard(props: ObjectReferenceProps & CardProps) {
    const { classes } = useStyles();

    const equipment_uuid = id_from_ref_props<string>(props)
    const api_handler = new EquipmentApi()
    const family_api_handler = new EquipmentFamiliesApi()
    const equipment_query = useQuery<AxiosResponse<Equipment>, AxiosError>({
        queryKey: ['equipment_retrieve', equipment_uuid],
        queryFn: () => api_handler.equipmentRetrieve(equipment_uuid)
    })
    const family_query = useQuery<AxiosResponse<EquipmentFamily>, AxiosError>({
        queryKey: ['equipment_family_retrieve', equipment_query.data?.data.family],
        queryFn: () => family_api_handler.equipmentFamiliesRetrieve(id_from_ref_props<string>(equipment_query.data!.data.family)),
        enabled: !!equipment_query.data?.data.family
    })

    const action = <Button
        variant="outlined"
        component={Link}
        to={`${PATHS.EQUIPMENT}/${equipment_uuid}`}
        startIcon={<ArrowForwardIcon/>}
    >View</Button>

    const loadingBody = <Card key={equipment_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS.EQUIPMENT}/${equipment_uuid}`}>{equipment_uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS.EQUIPMENT}>Equipment</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        <CardContent>
            <Grid container>
                <LoadingChip icon={<ICONS.EQUIPMENT/>} />
                <LoadingChip icon={<ICONS.EQUIPMENT/>} />
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
            </Grid>
        </CardContent>
    </Card>

    const cardBody = <Card key={equipment_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.EQUIPMENT/></Avatar>}
                title={<A component={Link} to={`${PATHS.EQUIPMENT}/${equipment_uuid}`}>
                    {`${family_query.data?.data.manufacturer} ${family_query.data?.data.model} ${equipment_query.data?.data.identifier}`}
                </A>}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS.EQUIPMENT}>Equipment</A>
                    <TeamChip url={equipment_query.data?.data.team!} sx={{fontSize: "smaller"}}/>
                </Stack>}
                action={action}
            />
            <CardContent>
                <Stack spacing={1}>
                    <Grid container>
                        <EquipmentFamilyChip url={equipment_query.data?.data.family!} />
                    </Grid>
                    <Grid container>
                        <Stack direction="row" spacing={1}>
                            <CountBadge
                                key={`cycler_tests`}
                                icon={<ICONS.CYCLER_TESTS/>}
                                badgeContent={equipment_query.data?.data.cycler_tests?.length || 0}
                                url={`${PATHS.CYCLER_TESTS}?equipment=${equipment_uuid}`}
                                tooltip={`Cycler Tests involving this Equipment`}
                            />
                        </Stack>
                    </Grid>
                </Stack>
            </CardContent>
        </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.EQUIPMENT/></Avatar>}
                title={equipment_uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS.EQUIPMENT}>Equipment</A>
                </Stack>}
            />
        }
        />

    return <QueryWrapper
        queries={[equipment_query, family_query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}