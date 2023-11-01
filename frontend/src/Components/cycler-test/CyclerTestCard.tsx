import useStyles from "../../UseStyles";
import {useQuery} from "@tanstack/react-query";
import {CyclerTestsApi} from "../../api_codegen";
import React from "react";
import CircularProgress from "@mui/material/CircularProgress";
import Card from "@mui/material/Card";
import clsx from "clsx";
import CardHeader from "@mui/material/CardHeader";
import A from "@mui/material/Link";
import {Link} from "react-router-dom";
import Stack from "@mui/material/Stack";
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import Button from "@mui/material/Button";
import ArrowForwardIcon from "@mui/icons-material/ArrowForward";
import {id_from_ref_props, ObjectReferenceProps, usePropParamId} from "../utils/misc";
import LoadingChip from "../utils/LoadingChip";
import {CardProps} from "@mui/material";
import ResourceChip from "../utils/ResourceChip";

export default function CyclerTestCard(props: ObjectReferenceProps & CardProps) {
    const {classes} = useStyles();

    const uuid = usePropParamId<string>(props)
    const query = useQuery({
        queryKey: ['cycler_tests_retrieve', uuid],
        queryFn: () => new CyclerTestsApi().cyclerTestsRetrieve(uuid)
    })

    const action = <Button
        variant="outlined"
        component={Link}
        to={`/cycler_tests/${uuid}`}
        startIcon={<ArrowForwardIcon/>}
    >View</Button>

    const loadingBody = <Card key={uuid} className={clsx(classes.item_card)} {...props as CardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`/cycler_tests/${uuid}`}>{uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={"/cycler_tests/"}>Cycler Test</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        <CardContent>
            <Grid container>
                <LoadingChip key="cells" icon={<ICONS.CELLS/>} />
                <LoadingChip key="schedule" icon={<ICONS.SCHEDULES/>} />
            </Grid>
            <Grid container>
                <LoadingChip key="equipment_1" icon={<ICONS.EQUIPMENT/>} />
                <LoadingChip key="equipment_2" icon={<ICONS.EQUIPMENT/>} />
            </Grid>
        </CardContent>
    </Card>

    const cardBody =
        <Card key={uuid} className={clsx(classes.item_card)} {...props as CardProps}>
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
                    <Grid container>
                        {query.data && <ResourceChip
                            lookup_key="CELL"
                            resource_id={id_from_ref_props<string>(query.data.data.cell!)}
                        />}
                        {query.data && <ResourceChip
                            lookup_key="SCHEDULE"
                            resource_id={id_from_ref_props<string>(query.data?.data.schedule!)}
                        />}
                    </Grid>
                    <Grid container>
                        {query.data?.data.equipment.map((equipment, i) =>
                            <ResourceChip
                                lookup_key="EQUIPMENT"
                                key={`equipment_${i}`}
                                resource_id={id_from_ref_props<string>(equipment)}
                            />)}
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

    return query.isLoading ? loadingBody : cardBody
}