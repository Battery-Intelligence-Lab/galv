import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CyclerTest, CyclerTestsApi} from "../../api_codegen";
import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Card, {CardProps} from "@mui/material/Card";
import clsx from "clsx";
import CardHeader from "@mui/material/CardHeader";
import A from "@mui/material/Link";
import {Link, useParams} from "react-router-dom";
import Stack from "@mui/material/Stack";
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import Button from "@mui/material/Button";
import EditIcon from "@mui/icons-material/Edit";
import ScheduleChip from "../schedule/ScheduleChip";
import EquipmentChip from "../equipment/EquipmentChip";
import CellChip from "../cell/CellChip";
import { PATHS } from "../../App";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import CellCard from "../cell/CellCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import ErrorPage from "../error/ErrorPage";
import {AxiosError, AxiosResponse} from "axios";
import ScheduleCard from "../schedule/ScheduleCard";
import EquipmentCard from "../equipment/EquipmentCard";

export default function CyclerTestPage(props: CardProps) {
    const {uuid} = useParams()
    const {classes} = useStyles();

    const query = useQuery<AxiosResponse<CyclerTest>, AxiosError>({
        queryKey: ['cycler_tests_retrieve', uuid],
        queryFn: () => new CyclerTestsApi().cyclerTestsRetrieve(uuid!),
        enabled: !!uuid
    })

    const action = <Stack direction="row" spacing={1}>
        <Button variant="outlined"
                component={Link}
                to={PATHS.CYCLER_TESTS}
                startIcon={<ArrowUpwardIcon/>}
        >All Cycler Tests</Button>
        {
            query.data?.data.permissions.write && <Button
                variant="outlined"
                component={Link}
                to={`/cycler_tests/${uuid}/edit`}
                startIcon={<EditIcon/>}
            >Edit</Button>
        }</Stack>

    const loadingBody = <Card key={uuid} className={clsx(classes.item_page)} elevation={0} {...props}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`/cycler_tests/${uuid}`}>{uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                Loading team info
            </Stack>}
            action={action}
        />
        <CardContent>
            Loading content
        </CardContent>
    </Card>

    const cardBody =
        <Card key={uuid} className={clsx(classes.item_page)} elevation={0} {...props}>
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CYCLER_TESTS/></Avatar>}
                title={<A component={Link} to={`/cycler_tests/${uuid}`}>{uuid}</A>}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                    <TeamChip url={query.data?.data.team!} sx={{fontSize: "smaller"}}/>
                </Stack>}
                action={action}
            />
            <CardContent>
                <Grid container spacing={2}>
                    <Grid xs={12} key="cell">
                        <CellCard url={query.data?.data.cell!}/>
                    </Grid>
                    <Grid container spacing={1} key="equipment">
                        {query.data?.data.equipment.map((equipment) =>
                            <Grid key={equipment}>
                                <EquipmentCard key={equipment} url={equipment}/>
                            </Grid>
                        )}
                    </Grid>
                    <Grid xs={12} key="schedule">
                        <ScheduleCard url={query.data?.data.schedule!}/>
                    </Grid>
                </Grid>
                {/*<details>*/}
                {/*    <summary>Raw data</summary>*/}
                <dl>
                    {query.data?.data && Object.entries(query.data.data)
                        .filter(([key, value]) => !['uuid'].includes(key))
                        .map(([key, value]) => (
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
                {/*</details>*/}
            </CardContent>
        </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorPage
        status={queries[0].failureReason?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CYCLER_TESTS/></Avatar>}
                title={uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                </Stack>}
            />}
    />

    return <QueryWrapper queries={[query]} error={getErrorBody} loading={loadingBody} success={cardBody} />
}