import {CardProps} from "@mui/material";
import {id_from_ref_props, ObjectReferenceProps} from "../component_utils";
import useStyles from "../../UseStyles";
import {Cell, CellFamiliesApi, CellFamily, CellsApi} from "../../api_codegen";
import {useQuery} from "@tanstack/react-query";
import Card from "@mui/material/Card";
import Button from "@mui/material/Button";
import {Link, useParams} from "react-router-dom";
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
import React from "react";
import ErrorPage from "../error/ErrorPage";
import QueryWrapper, {QueryDependentElement} from "../QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import CellFamilyChip from "./CellFamilyChip";
import CountBadge from "../CountBadge";
import {PATHS} from "../../App";

export default function CellPage(props: CardProps) {
    const { classes } = useStyles();

    const cell_uuid = useParams().uuid!
    const api_handler = new CellsApi()
    const family_api_handler = new CellFamiliesApi()
    const cell_query = useQuery<AxiosResponse<Cell>, AxiosError>({
        queryKey: ['cell_retrieve', cell_uuid],
        queryFn: () => api_handler.cellsRetrieve(cell_uuid)
    })
    const family_query = useQuery<AxiosResponse<CellFamily>, AxiosError>({
        queryKey: ['cell_family_retrieve', cell_query.data?.data.family],
        queryFn: () => family_api_handler.cellFamiliesRetrieve(id_from_ref_props<string>(cell_query.data!.data.family)),
        enabled: !!cell_query.data?.data.family
    })

    const action = <Button
        variant="outlined"
        component={Link}
        to={`/cycler_tests/${cell_uuid}`}
        startIcon={<ArrowForwardIcon/>}
    >View</Button>

    const loadingBody =
        <Card key={cell_uuid} className={clsx(classes.item_page)} elevation={0} {...props}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`/cycler_tests/${cell_uuid}`}>{cell_uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        <CardContent>
            <Grid container>
                <LoadingChip icon={<ICONS.CELLS/>} />
                <LoadingChip icon={<ICONS.SCHEDULES/>} />
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>} />
            </Grid>
        </CardContent>
    </Card>

    const cardBody =
        <Card key={cell_uuid} className={clsx(classes.item_page)} elevation={0} {...props}>
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
                title={<A component={Link} to={`/cells/${cell_uuid}`}>
                    {`${family_query.data?.data.manufacturer} ${family_query.data?.data.model} ${cell_query.data?.data.identifier}`}
                </A>}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={"/cell/"}>Cell</A>
                    <TeamChip url={cell_query.data?.data.team!} sx={{fontSize: "smaller"}}/>
                </Stack>}
                action={action}
            />
            <CardContent>
                <Stack>
                    <Grid container>
                        <CellFamilyChip url={cell_query.data?.data.family!} />
                    </Grid>
                    <Grid container>
                        <Stack direction="row" spacing={1}>
                            <CountBadge
                                key={`cycler_tests`}
                                icon={<ICONS.CYCLER_TESTS/>}
                                badgeContent={cell_query.data?.data.cycler_tests?.length || 0}
                                url={`${PATHS.CYCLER_TESTS}?cell=${cell_uuid}`}
                                tooltip={`Cycler Tests`}
                            />
                        </Stack>
                    </Grid>
                </Stack>
                <details>
                    <summary>Raw data</summary>
                    <dl>
                        {cell_query.data?.data && Object.entries(cell_query.data.data)
                            .filter(([key, value]) => !['uuid'].includes(key))
                            .map(([key, value]: any) => (
                                <div key={key}>
                                    <dt>{key}</dt>
                                    <dd>{value instanceof Array ?
                                        (<ul>{value.map((v, i) => <li key={i}>{v}</li>)}</ul>) :
                                        typeof value === 'object' ?
                                            Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(", ") :
                                            value}</dd>
                                </div>
                            ))}
                    </dl>
                </details>
            </CardContent>
        </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorPage
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
                title={cell_uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={"/cell/"}>Cell</A>
                </Stack>}
            />
        }
        />

    return <QueryWrapper
        queries={[cell_query, family_query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}