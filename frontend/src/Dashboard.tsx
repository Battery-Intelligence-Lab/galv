import {DISPLAY_NAMES_PLURAL, ICONS, LOOKUP_KEYS, LookupKey} from "./constants";
import axios, {AxiosError, AxiosResponse} from "axios";
import {useQuery, useQueryClient} from "@tanstack/react-query";
import {
    FilesApi,
    ObservedFile, PaginatedObservedFileList,
    PaginatedSchemaValidationList,
    SchemaValidation,
    SchemaValidationsApi
} from "./api_codegen";
import {get_url_components, id_from_ref_props} from "./Components/misc";
import LookupKeyIcon from "./Components/LookupKeyIcon";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItem from "@mui/material/ListItem";
import Tooltip from "@mui/material/Tooltip";
import {ResourceChip} from "./Components/ResourceChip";
import Stack from "@mui/material/Stack";
import React, {ReactNode, useState} from "react";
import Button from "@mui/material/Button";
import {useCurrentUser} from "./Components/CurrentUserContext";
import List from "@mui/material/List";
import {SvgIconProps} from "@mui/material/SvgIcon";
import CardHeader from "@mui/material/CardHeader";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Typography from "@mui/material/Typography";
import Container from "@mui/material/Container";
import Chip from "@mui/material/Chip";
import Representation from "./Components/Representation";
import ListSubheader from "@mui/material/ListSubheader";

type SchemaValidationSummary = {
    detail: SchemaValidation
    lookup_key?: LookupKey
    resource_id?: string
}

const get_color = (status: SchemaValidation["status"]) => {
    switch (status) {
        case "VALID":
            return "success"
        case "ERROR":
            return "error"
        case "INVALID":
            return "warning"
        default:
            return undefined
    }
}

function StatusIcon(
    {status, count, ...props}: {status: SchemaValidation["status"], count?: number} & SvgIconProps
) {
    const ICON = ICONS[`validation_status_${status}` as keyof typeof ICONS]
    const color = get_color(status)
    return count? <Chip icon={<ICON color={color} {...props}/>} label={count} /> : <ICON color={color} {...props}/>
}

function KeySummary(
    {lookupKey, data}:
        {lookupKey: LookupKey, data: SchemaValidationSummary[]}
) {
    const status_counts: {[key in SchemaValidation["status"]]?: {[schema_id: string]: number}} = {}
    data.forEach(d => {
        const id = id_from_ref_props<string>(d.detail.schema)
        if (status_counts[d.detail.status] === undefined)
            status_counts[d.detail.status] = {[id]: 1}
        else {
            const s = status_counts[d.detail.status]!
            if (s[id] === undefined)
                s[id] = 1
            else
                s[id]++
        }
    })

    const [open, setOpen] = useState(false);

    const tooltip = (status: SchemaValidation["status"]) => <List>
        <ListSubheader>{status}</ListSubheader>
        {status_counts[status] && Object.entries(status_counts[status]!).map(([schema_id, count]) =>
            <ListItem key={schema_id}>
                <ListItemText key="count">
                    <Representation resource_id={schema_id} lookup_key={LOOKUP_KEYS.VALIDATION_SCHEMA} />: {count}
                </ListItemText>
            </ListItem>
        )}
    </List>

    const hasContent = data.filter(d => ["ERROR", "INVALID"].includes(d.detail.status)).length > 0

    return <Card>
        <CardHeader
            onClick={() => setOpen(!open)}
            sx={{cursor: hasContent? "pointer" : undefined}}
            avatar={<LookupKeyIcon lookupKey={lookupKey} />}
            title={DISPLAY_NAMES_PLURAL[lookupKey]}
            action={<Stack direction="row" spacing={1} alignItems="center">{Object.keys(status_counts).map(status => <Tooltip
                    key={status}
                    title={tooltip(status as SchemaValidation["status"])}
                    placement="left"
                    arrow
                >
                    <div>
                        <StatusIcon
                            status={status as SchemaValidation["status"]}
                            count={status_counts[status as keyof typeof status_counts] &&
                                Object.entries(status_counts[status as keyof typeof status_counts]!)
                                    .reduce((a, [_, b]) => a + b, 0)}
                        />
                    </div>
                </Tooltip>
            )}
            </Stack>
            }
            subheader={(!open && hasContent) ? "Click for details of failed validations" : ""}
        />
        {open && hasContent && <CardContent>
            <List>
                {data.filter(d => ["ERROR", "INVALID"].includes(d.detail.status))
                    .map(d => d.resource_id)
                    .filter((id, i, a) => a.indexOf(id) === i)
                    .filter((id): id is string => id !== undefined)
                    .map(id => <ListItem key={id}>
                        <Stack>
                            <ResourceChip resource_id={id} lookup_key={lookupKey} short_name={false} />
                            <List>
                                {data.filter(d => d.resource_id === id && ["ERROR", "INVALID"].includes(d.detail.status))
                                    .map(d => <ListItem key={d.detail.schema}>
                                        <ListItemIcon><StatusIcon status={d.detail.status}/></ListItemIcon>
                                        <ResourceChip
                                            resource_id={id_from_ref_props(d.detail.schema)}
                                            lookup_key={LOOKUP_KEYS.VALIDATION_SCHEMA}
                                        />
                                        <Typography>{d.detail.detail?.message ?? "No further information"}</Typography>
                                    </ListItem>)
                                }
                            </List>
                        </Stack>
                    </ListItem>)
                }
            </List>
        </CardContent>}
    </Card>
}

export function SchemaValidationList() {

    const {setLoginFormOpen} = useCurrentUser()

    // API handler
    const api_handler = new SchemaValidationsApi()
    // Queries
    const queryClient = useQueryClient()
    const query = useQuery<AxiosResponse<PaginatedSchemaValidationList>, AxiosError, SchemaValidationSummary[]>({
        queryKey: ["SCHEMA_VALIDATION", 'list'],
        queryFn: () => api_handler.schemaValidationsList().then((r): typeof r => {
            try {
                // Update the cache for each resource
                r.data.results?.forEach((resource: SchemaValidation) => {
                    queryClient.setQueryData(["SCHEMA_VALIDATION", resource.id], {...r, data: resource})
                })
            } catch (e) {
                console.error("Error updating cache from list data.", e)
            }
            return r
        }),
        select: (data) => {
            const out: SchemaValidationSummary[] = []
            data.data.results?.forEach((resource: SchemaValidation) => {
                out.push({detail: resource, ...get_url_components(resource.validation_target)})
            })
            return out
        }
    })

    let body: ReactNode|null = null
    if (!query.data)
        body = <p>Loading...</p>
    else if (query.data.length === 0)
        body = !axios.defaults.headers.common['Authorization']?
            <p>
                <Button onClick={() => setLoginFormOpen(true)}>
                    Log in
                </Button> to see your dashboard.
            </p> :
            <p>
                There's nothing to show on your dashboard yet.
                When you're added to some teams you'll see the status of your data and metadata here.
            </p>

    return <Container maxWidth="lg">
        {body || <Stack spacing={1}>
            {query.data &&
                query.data.map(d => d.lookup_key)
                    .filter((k, i, a) => a.indexOf(k) === i)
                    .filter((k): k is LookupKey => k !== undefined)
                    .map((k) => <KeySummary
                        key={k}
                        lookupKey={k}
                        data={query.data.filter(d => d.lookup_key === k)}
                    />)
            }
        </Stack>}
    </Container>
}

export function DatasetStatus() {
    // API handler
    const api_handler = new FilesApi()
    // Queries
    const queryClient = useQueryClient()
    const query = useQuery<AxiosResponse<PaginatedObservedFileList>, AxiosError>({
        queryKey: [LOOKUP_KEYS.FILE, 'list'],
        queryFn: () => api_handler.filesList().then((r): typeof r => {
            try {
                // Update the cache for each resource
                r.data.results?.forEach((resource: ObservedFile) => {
                    queryClient.setQueryData(["SCHEMA_VALIDATION", resource.uuid], {...r, data: resource})
                })
            } catch (e) {
                console.error("Error updating cache from list data.", e)
            }
            return r
        })
    })

    const state_to_status = (state: ObservedFile["state"]) => {
        return state === "IMPORTED"? "VALID" :
            state === "IMPORT FAILED" ?
                "ERROR" : "UNCHECKED"
    }

    const status_counts = query.data && query.data.data.results?.reduce(
        (a, b) => {
            const status = state_to_status(b.state)
            if (a[status] === undefined)
                a[status] = {[b.state]: 1}
            else {
                if (a[status]![b.state] === undefined)
                    a[status]![b.state] = 1
                else
                    a[status]![b.state]!++
            }
            return a
        },
        {} as {[key in ReturnType<typeof state_to_status>]: {[key in ObservedFile["state"]]?: number}}
    )

    const TooltipContent = ({status}: {status: ReturnType<typeof state_to_status>}) => {
        return <List>
            {status_counts && Object.entries(status_counts[status]!).map(([state, count]) =>
                <ListItem key={state}>
                    <ListItemText>{state}: {count}</ListItemText>
                </ListItem>
            )}
        </List>
    }

    return <Container maxWidth="lg">
        {query.isLoading? "Loading..." : <Card>
            <CardHeader
                avatar={<LookupKeyIcon lookupKey={LOOKUP_KEYS.FILE} />}
                title={DISPLAY_NAMES_PLURAL[LOOKUP_KEYS.FILE]}
                action={<Stack direction="row" spacing={1} alignItems="center">
                    {status_counts &&
                        Object.entries(status_counts).map(([status, counts]) => <Tooltip
                            title={<TooltipContent status={status as ReturnType<typeof state_to_status>} />}
                            key={status}
                            placement="left"
                            arrow
                        >
                            <div>
                                <StatusIcon
                                    key={status}
                                    status={status as SchemaValidation["status"]}
                                    count={Object.entries(counts).reduce((a, [_, b]) => a + b, 0)}
                                />
                            </div>
                        </Tooltip>)}
                </Stack>}
            />
        </Card>}

    </Container>
}

export default function Dashboard() {
    return <Stack spacing={2}>
        <Typography variant={"h6"} sx={{paddingLeft: "1em"}}>Harvested Files</Typography>
        <DatasetStatus />
        <Typography variant={"h6"} sx={{paddingLeft: "1em"}}>Metadata Validations</Typography>
        <SchemaValidationList />
    </Stack>
}