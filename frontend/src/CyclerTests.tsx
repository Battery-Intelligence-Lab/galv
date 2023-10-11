// SPDX-License-Identifier: BSD-2-Clause
// Copyright  (c) 2020-2023, The Chancellor, Masters and Scholars of the University
// of Oxford, and the 'Galv' Developers. All rights reserved.

import React from "react";
import useStyles from "./UseStyles";
import {useQuery} from "@tanstack/react-query";
import {
    CyclerTest,
    CyclerTestsApi,
    EquipmentApi,
    EquipmentFamiliesApi,
    ScheduleFamiliesApi,
    SchedulesApi
} from "./api_codegen";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import {Link} from "react-router-dom";
import axios from "axios";
import Divider from "@mui/material/Divider";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardActions from "@mui/material/CardActions";
import {id_from_url} from "./AxiosConfig";
import {ICONS} from "./icons";
import Chip from "@mui/material/Chip";
import Stack from "@mui/material/Stack";

type ScheduleOneLineProps = {
    url: string
}
type EquipmentOneLineProps = {
    url: string
}

function ScheduleOneLine(props: ScheduleOneLineProps) {
    const schedule_uuid = id_from_url(props.url)
    const api_handler = new SchedulesApi()
    const family_api_handler = new ScheduleFamiliesApi()
    const schedule_query = useQuery({
        queryKey: [`schedule_get_${schedule_uuid}`],
        queryFn: () => api_handler.schedulesRetrieve(schedule_uuid)
    })
    const family_query = useQuery({
        queryKey: [`schedule_family_get_${schedule_query.data?.data.family}`],
        queryFn: () => family_api_handler.scheduleFamiliesRetrieve(id_from_url(schedule_query.data!.data.family)),
        enabled: !!schedule_query.data?.data.family
    })
    return (
        <Chip
            key={schedule_uuid}
            icon={<ICONS.SCHEDULES />}
            variant="outlined"
            label={family_query.data?.data.identifier}
            clickable={true}
            component='a'
            href={`/schedules/${schedule_uuid}`}
        />
    )
}

function EquipmentOneLine(props: EquipmentOneLineProps) {
    const equipment_uuid = id_from_url(props.url)
    const api_handler = new EquipmentApi()
    const family_api_handler = new EquipmentFamiliesApi()
    const equipment_query = useQuery({
        queryKey: [`equipment_get_${equipment_uuid}`],
        queryFn: () => api_handler.equipmentRetrieve(equipment_uuid)
    })
    const family_query = useQuery({
        queryKey: [`equipment_family_get_${equipment_query.data?.data.family}`],
        queryFn: () => family_api_handler.equipmentFamiliesRetrieve(id_from_url(equipment_query.data!.data.family)),
        enabled: !!equipment_query.data?.data.family
    })
    return (
        <Chip
            key={equipment_uuid}
            icon={<ICONS.EQUIPMENT />}
            variant="outlined"
            label={`${family_query.data?.data.type}: ${family_query.data?.data.manufacturer} ${family_query.data?.data.model}`}
            clickable={true}
            component='a'
            href={`/equipment/${equipment_uuid}`}
        />
    )
}

function CyclerTestThreeLine(cyclerTest: CyclerTest, classes: Record<string, string>) {
    return (
        <Container key={cyclerTest.uuid}>
            <Card>
                <CardContent>
                    <Typography variant="h5" component="h2">
                        ID: <Link to={`/cycler_tests/${cyclerTest.uuid}`}>{cyclerTest.uuid}</Link>
                    </Typography>
                    <ScheduleOneLine url={cyclerTest.schedule} />
                    <Stack direction="row" spacing={1}>
                        {cyclerTest.equipment.map((equipment) => <EquipmentOneLine url={equipment} />)}
                    </Stack>
                    <Divider />
                    <dl>
                        {Object.entries(cyclerTest)
                            .filter(([key, value]) => !['uuid'].includes(key))
                            .map(([key, value]) => (
                                <div key={key}>
                                    <dt>{key}</dt>
                                    <dd>{
                                        value instanceof Array?
                                            (<ul>{value.map((v, i) => <li key={i}>{v}</li>)}</ul>) :
                                            typeof value === 'object'?
                                                Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(", ") :
                                                value
                                    }</dd>
                                </div>
                            ))}
                    </dl>
                </CardContent>
                <CardActions>
                    <Link to={`/cycler_tests/${cyclerTest.uuid}`}>View</Link>
                </CardActions>
            </Card>
        </Container>
    )
}

export default function CyclerTests() {
    const { classes } = useStyles();

    // API handler
    const api_handler = new CyclerTestsApi()
    // Queries
    const query = useQuery({
        queryKey: ['cycler_tests_list'],
        queryFn: () => api_handler.cyclerTestsList()
    })

    return (
        <Container maxWidth="lg" className={classes.container}>
            <Typography
                component="h1"
                variant="h3"
                className={[classes.page_title, classes.text].join(" ")}
            >Cycler Tests {query.isLoading && <span>...</span>}</Typography>
            {
                query.isInitialLoading && <p>Loading...</p>
            }
            { query.data?.data?.results && query.data.data.results.length === 0 ?
                !axios.defaults.headers.common['Authorization']?
                    <p><Link to="/login">Log in</Link> to see Cycler Tests</p> :
                    <p>No Cycler Tests found</p> :
                query.data?.data?.results?.map((cycler_test: CyclerTest) => CyclerTestThreeLine(cycler_test, classes))
            }
        </Container>
    );
}
