import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CyclerTestsApi} from "../../api_codegen";
import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Card from "@mui/material/Card";
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

export default function CyclerTestPage() {
    const {uuid} = useParams()
    const {classes} = useStyles();

    const query = useQuery({
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

    const loadingBody = <Card key={uuid} className={clsx(classes.item_page)} elevation={0}>
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
        <Card key={uuid} className={clsx(classes.item_page)} elevation={0}>
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
                <Stack>
                    <CellCard url={query.data?.data.cell_subject!}/>
                    <Grid container>
                        <CellChip url={query.data?.data.cell_subject!}/>
                        <ScheduleChip url={query.data?.data.schedule!}/>
                    </Grid>
                    <Grid container>
                        {query.data?.data.equipment.map((equipment) => <EquipmentChip url={equipment}/>)}
                    </Grid>
                </Stack>
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

    return query.isLoading ? loadingBody : cardBody
}