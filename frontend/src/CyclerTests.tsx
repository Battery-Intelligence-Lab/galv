// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React, {Component, useState} from "react";
import useStyles from "./UseStyles";
import {useQuery} from "@tanstack/react-query";
import {
    CellFamiliesApi,
    CellsApi,
    CyclerTest,
    CyclerTestsApi,
    EquipmentApi,
    EquipmentFamiliesApi, LabsApi,
    ScheduleFamiliesApi,
    SchedulesApi, TeamsApi
} from "./api_codegen";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import {Link, useNavigate} from "react-router-dom";
import A from "@mui/material/Link";
import axios from "axios";
import Divider from "@mui/material/Divider";
import Card from "@mui/material/Card";
import CardHeader from "@mui/material/CardHeader";
import CardContent from "@mui/material/CardContent";
import {ICONS} from "./icons";
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import Chip, {ChipProps} from "@mui/material/Chip";
import Stack from "@mui/material/Stack";
import clsx from "clsx";
import Avatar from "@mui/material/Avatar";
import Grid from "@mui/material/Unstable_Grid2";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import LinearProgress from "@mui/material/LinearProgress";
import Skeleton from "@mui/material/Skeleton";
import {withStyles} from "tss-react/mui";
import {AsyncTableProps} from "./AsyncTable";
import TextField from "@mui/material/TextField";
import FilterBar from "./filtering/FilterBar";
import TextFilter from "./filtering/TextFilter";

type ObjectReferenceProps =
    { uuid: string } |
    { id: number } |
    { url: string }


const linear = <LinearProgress sx={{color: (t) => t.palette.text.disabled}} />
const circular = <LinearProgress sx={{color: (t) => t.palette.text.disabled}} />

function id_from_ref_props<T extends number|string>(props: ObjectReferenceProps|string|number): T {
    if (typeof props === 'number')
        return props as T
    if (typeof props === 'object') {
        if ('uuid' in props) {
            return props.uuid as T
        } else if ('id' in props) {
            return props.id as T
        }
    }
    const url = typeof props === 'string'? props : props.url
    try {
        const id = url.split('/').filter(x => x).pop()
        if (id !== undefined) return id as T
    } catch (e) {
        throw new Error(`Could not parse id from url: ${url}: ${e}`)
    }
    throw new Error(`Could not parse id from url: ${url}`)
}

function ScheduleChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

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

    return schedule_query.isLoading?
        <LoadingChip url={`/schedules/${schedule_uuid}`} icon={<ICONS.SCHEDULES/>} {...props}/> :
        <Chip
            key={schedule_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.SCHEDULES />}
            variant="outlined"
            label={family_query.isLoading? '...' : family_query.data?.data.identifier}
            clickable={true}
            component={Link}
            to={`/schedules/${schedule_uuid}`}
            {...props as ChipProps as any}
        />
}

function CellChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();

    const cell_uuid = id_from_ref_props<string>(props)
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

function EquipmentChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();
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
    return equipment_query.isLoading?
        <LoadingChip url={`/equipment/${equipment_uuid}`} icon={<ICONS.EQUIPMENT/>} {...props}/> :
        <Chip
            key={equipment_uuid}
            className={clsx(classes.item_chip)}
            icon={<ICONS.EQUIPMENT />}
            variant="outlined"
            label={
                equipment_query.isLoading || family_query.isLoading? '...' :
                    `${family_query.data?.data.type}: ${family_query.data?.data.manufacturer} ${family_query.data?.data.model}`
            }
            clickable={true}
            component={Link}
            to={`/equipment/${equipment_uuid}`}
            {...props as ChipProps as any}
        />
}

function TeamChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();
    const team_id = id_from_ref_props<number>(props)
    const api_handler = new TeamsApi()
    const team_query = useQuery({
        queryKey: ['teams_retrieve', team_id],
        queryFn: () => api_handler.teamsRetrieve(team_id)
    })
    return team_query.isLoading?
        <LoadingChip url={`/teams/${team_id}`} icon={<ICONS.TEAMS/>} {...props}/> :
        team_query.isError? <LabChip {...props}/> : <Chip
            key={team_id}
            className={clsx(classes.item_chip, classes.team_chip)}
            icon={<ICONS.TEAMS />}
            variant="outlined"
            label={team_query.isLoading? '...' : team_query.data?.data.name}
            clickable={true}
            component={Link}
            to={`/teams/${team_id}`}
            {...props as ChipProps as any}
        />
}

function LabChip(props: ObjectReferenceProps & ChipProps) {
    const { classes } = useStyles();
    const lab_id = id_from_ref_props<number>(props)
    const api_handler = new LabsApi()
    const lab_query = useQuery({
        queryKey: ['labs_retrieve', lab_id],
        queryFn: () => api_handler.labsRetrieve(lab_id)
    })
    return lab_query.isLoading? <LoadingChip url={`labs/${lab_id}`} icon={<ICONS.LABS />}/> :
        <Chip
            key={lab_id}
            className={clsx(classes.item_chip, classes.team_chip)}
            icon={<ICONS.LABS />}
            variant="outlined"
            label={lab_query.isLoading? '...' : lab_query.data?.data.name}
            clickable={true}
            component={Link}
            to={`/labs/${lab_id}`}
            {...props as ChipProps as any}
        />
}

function LoadingChip(props: {url: string, icon: JSX.Element} & ChipProps) {
    const { classes } = useStyles();
    return <Chip
        key={id_from_ref_props<string>(props)}
        className={clsx(classes.item_chip)}
        variant="outlined"
        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
        component={Link}
        icon={props.icon}
        to={props.url}
        clickable={true}
        {...props as ChipProps as any}
    />
}

function CyclerTestThreeLine(props: ObjectReferenceProps) {
    const { classes } = useStyles();
    const navigate = useNavigate();

    const uuid = id_from_ref_props<string>(props)
    const query = useQuery({
        queryKey: ['cycler_tests_retrieve', uuid],
        queryFn: () => new CyclerTestsApi().cyclerTestsRetrieve(uuid)
    })

    const loadingBody = <Container key={uuid}>
        <Card className={clsx(classes.item_card)}>
            <CardHeader
                avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
                title={<A component={Link} to={`/cycler_tests/${uuid}`}>{uuid}</A>}
                subheader={<Stack direction="row" spacing={1}>
                    <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                    <Chip
                        icon={<ICONS.LABS/>}
                        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
                        className={classes.item_chip}
                    />
                </Stack>}
                action={<Link to={`/cycler_tests/${uuid}`}>View</Link>}
            />
            <CardContent>
                <Grid container>
                    <Chip
                        icon={<ICONS.CELLS/>}
                        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
                        className={classes.item_chip}
                    />
                    <Chip
                        icon={<ICONS.SCHEDULES/>}
                        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
                        className={classes.item_chip}
                    />
                </Grid>
                <Grid container>
                    <Chip
                        icon={<ICONS.EQUIPMENT/>}
                        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
                        className={classes.item_chip}
                    />
                    <Chip
                        icon={<ICONS.EQUIPMENT/>}
                        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
                        className={classes.item_chip}
                    />
                </Grid>
            </CardContent>
        </Card>
    </Container>

    const cardBody =
        <Card key={uuid} className={clsx(classes.item_card)}>
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CYCLER_TESTS/></Avatar>}
                title={<A component={Link} to={`/cycler_tests/${uuid}`}>{uuid}</A>}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                    <TeamChip url={query.data?.data.team!} sx={{fontSize: "smaller"}}/>
                </Stack>}
                action={<Button
                    variant="outlined"
                    component={Link}
                    to={`/cycler_tests/${uuid}`}
                    startIcon={<ArrowForwardIcon />}
                >View</Button>}
            />
            <CardContent>
                <Stack>
                    <Grid container>
                        <CellChip url={query.data?.data.cell_subject!} />
                        <ScheduleChip url={query.data?.data.schedule!} />
                    </Grid>
                    <Grid container>
                        {query.data?.data.equipment.map((equipment) => <EquipmentChip url={equipment}/>)}
                    </Grid>
                </Stack>
                {/*<details>*/}
                {/*    <summary>Raw data</summary>*/}
                {/*    <dl>*/}
                {/*        {query.data?.data && Object.entries(query.data.data)*/}
                {/*            .filter(([key, value]) => !['uuid'].includes(key))*/}
                {/*            .map(([key, value]) => (*/}
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

    return query.isLoading? loadingBody : cardBody
}



export default function CyclerTests() {
    const { classes } = useStyles();
    const [filteredData, setFilteredData] = useState<CyclerTest[]>([])

    // API handler
    const api_handler = new CyclerTestsApi()
    // Queries
    const query = useQuery({
        queryKey: ['cycler_tests_list'],
        queryFn: () => api_handler.cyclerTestsList()
    })

    return (
        <Container maxWidth="lg" className={classes.container}>
            <Grid container justifyContent="space-between">
                <Typography
                    component="h1"
                    variant="h3"
                    className={clsx(classes.page_title, classes.text)}
                >
                    Cycler Tests
                    {query.isLoading && <CircularProgress sx={{color: (t) => t.palette.text.disabled, marginLeft: "1em"}} />}
                </Typography>
                <FilterBar
                    data={query.data?.data?.results}
                    filters={{uuid: {target_key: 'uuid', label: 'UUID matches', widget: TextFilter}}}
                    setFilteredData={setFilteredData}
                />
            </Grid>
            <Stack spacing={2}>
                {
                    query.isInitialLoading && [1, 2, 3, 4, 5].map((i) =>
                        <Skeleton key={i} variant="rounded" height="6em"/>
                    )
                }
                { query.data?.data?.results && query.data.data.results.length === 0 ?
                    !axios.defaults.headers.common['Authorization']?
                        <p><Link to="/login">Log in</Link> to see Cycler Tests</p> :
                        <p>No Cycler Tests found</p> :
                    filteredData.map(
                        (cycler_test: CyclerTest) => <CyclerTestThreeLine uuid={cycler_test.uuid} />
                    )
                }
            </Stack>
        </Container>
    );
}
