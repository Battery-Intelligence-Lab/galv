import {CardProps} from "@mui/material";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import useStyles from "../../UseStyles";
import {Schedule, ScheduleFamiliesApi, ScheduleFamily, SchedulesApi} from "../../api_codegen";
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
import LoadingChip from "../LoadingChip";
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import ScheduleFamilyChip from "./ScheduleFamilyChip";
import React from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import CountBadge from "../CountBadge";
import {PATHS} from "../../App";
import CheckIcon from "@mui/icons-material/Check";

export default function ScheduleCard(props: ObjectReferenceProps & CardProps) {
    const { classes } = useStyles();

    const schedule_uuid = id_from_ref_props<string>(props)
    const api_handler = new SchedulesApi()
    const family_api_handler = new ScheduleFamiliesApi()
    const schedule_query = useQuery<AxiosResponse<Schedule>, AxiosError>({
        queryKey: ['schedule_retrieve', schedule_uuid],
        queryFn: () => api_handler.schedulesRetrieve(schedule_uuid)
    })
    const family_query = useQuery<AxiosResponse<ScheduleFamily>, AxiosError>({
        queryKey: ['schedule_family_retrieve', schedule_query.data?.data.family],
        queryFn: () => family_api_handler.scheduleFamiliesRetrieve(id_from_ref_props<string>(schedule_query.data!.data.family)),
        enabled: !!schedule_query.data?.data.family
    })

    const action = <Button
        variant="outlined"
        component={Link}
        to={`${PATHS.SCHEDULES}/${schedule_uuid}`}
        startIcon={<ArrowForwardIcon/>}
    >View</Button>

    const loadingBody = <Card key={schedule_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS.SCHEDULES}/${schedule_uuid}`}>{schedule_uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS.SCHEDULES}>Schedule</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        <CardContent>
            <Grid container>
                <LoadingChip icon={<ICONS.SCHEDULES/>} />
                <LoadingChip icon={<ICONS.SCHEDULES/>} />
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
            </Grid>
        </CardContent>
    </Card>

    const cardBody = <Card key={schedule_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.SCHEDULES/></Avatar>}
                title={<A component={Link} to={`${PATHS.SCHEDULES}/${schedule_uuid}`}>
                    {`${family_query.data?.data.identifier} ${schedule_uuid}`}
                </A>}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS.SCHEDULES}>Schedule</A>
                    <TeamChip url={schedule_query.data?.data.team!} sx={{fontSize: "smaller"}}/>
                </Stack>}
                action={action}
            />
            <CardContent>
                <Stack spacing={1}>
                    <Grid container>
                        <ScheduleFamilyChip url={schedule_query.data?.data.family!} />
                    </Grid>
                    <Grid container>
                        <Stack direction="row" spacing={1}>
                            <CountBadge
                                key="files"
                                icon={<ICONS.FILES/>}
                                badgeContent={schedule_query.data?.data.schedule_file? <CheckIcon/> : 0}
                                url={`${PATHS.SCHEDULES}/${schedule_uuid}/files`}
                                tooltip={`Schedule File`}
                            />
                            <CountBadge
                                key={`cycler_tests`}
                                icon={<ICONS.CYCLER_TESTS/>}
                                badgeContent={schedule_query.data?.data.cycler_tests?.length || 0}
                                url={`${PATHS.CYCLER_TESTS}?schedule=${schedule_uuid}`}
                                tooltip={`Cycler Tests involving this Schedule`}
                            />
                        </Stack>
                    </Grid>
                </Stack>
                {/*<details>*/}
                {/*    <summary>Raw data</summary>*/}
                {/*    <dl>*/}
                {/*        {schedule_query.data?.data && Object.entries(schedule_query.data.data)*/}
                {/*            .filter(([key, value]) => !['uuid'].includes(key))*/}
                {/*            .map(([key, value]: any) => (*/}
                {/*                <div key={key}>*/}
                {/*                    <dt>{key}</dt>*/}
                {/*                    <dd>{value instanceof Array ?*/}
                {/*                        (<ul>{value.map((v, i) => <li key={i}>{v}</li>)}</ul>) :*/}
                {/*                        typeof value === 'object' ?*/}
                {/*                            Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(", ") :*/}
                {/*                            value}</dd>*/}
                {/*                </div>*/}
                {/*            ))}*/}
                {/*    </dl>*/}
                {/*</details>*/}
            </CardContent>
        </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.SCHEDULES/></Avatar>}
                title={schedule_uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS.SCHEDULES}>Schedule</A>
                </Stack>}
            />
        }
        />

    return <QueryWrapper
        queries={[schedule_query, family_query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}