import {DISPLAY_NAMES_PLURAL, ICONS, LookupKey, PATHS} from "./constants";
import useStyles from "./styles/UseStyles";
import {AxiosError, AxiosResponse} from "axios";
import {useQuery, useQueryClient} from "@tanstack/react-query";
import {PaginatedSchemaValidationList, SchemaValidation, SchemaValidationsApi} from "./api_codegen";
import {get_url_components} from "./Components/misc";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableHead from "@mui/material/TableHead";
import TableBody from "@mui/material/TableBody";
import clsx from "clsx";
import LookupKeyIcon from "./Components/LookupKeyIcon";
import {Link} from "react-router-dom";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import ListItem from "@mui/material/ListItem";
import Tooltip from "@mui/material/Tooltip";
import {ResourceChip} from "./Components/ResourceChip";
import Stack from "@mui/material/Stack";
import {useState} from "react";

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

function StatusSummary(
    {lookupKey, data, statuses}:
        {lookupKey: LookupKey, data?: SchemaValidationSummary[], statuses: SchemaValidation["status"][]}
) {
    const subset = data? data.filter(d => d.lookup_key === lookupKey) : []
    const status_counts: {[key in SchemaValidation["status"]]?: number} = {}
    subset.forEach(d => status_counts[d.detail.status] = (status_counts[d.detail.status] || 0) + 1)

    const [open, setOpen] = useState(false);

    return <TableRow>
        <TableCell key="label">
            <Link to={PATHS[lookupKey]}>
                <ListItem>
                    <ListItemIcon key="icon"><LookupKeyIcon lookupKey={lookupKey} /></ListItemIcon>
                    <ListItemText key="text">
                        {DISPLAY_NAMES_PLURAL[lookupKey]}
                    </ListItemText>
                </ListItem>
            </Link>
        </TableCell>
        <TableCell key="details" onClick={() => setOpen(!open)}>
            <Tooltip title="Click to show resources" describeChild={true}>
                {open? <ICONS.EXPAND_LESS fontsize="large" /> : <ICONS.EXPAND_MORE fontSize="large"/>}
            </Tooltip>
        </TableCell>
        {statuses.map(status => <TableCell
            className={clsx(`status_summary_${status}`)}
            key={status}
        >
            {status_counts[status] || 0}
            {open && <Stack>
                {subset.filter(d => d.detail.status === status)
                        .map(d => d.resource_id)
                        .filter((id): id is string => id !== undefined)
                        .map(id => <ResourceChip
                            key={id}
                            lookup_key={lookupKey}
                            resource_id={id}
                        />)}
            </Stack>}
        </TableCell>)}
    </TableRow>
}

export default function Dashboard() {
    const { classes } = useStyles();

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

    const statuses = query.data?.map(d => d.detail.status)
        .filter((s, i, a) => a.indexOf(s) === i) as SchemaValidation["status"][] ?? []

    return <TableContainer>
        <Table>
            <TableHead>
                <TableRow>
                    <TableCell />
                    <TableCell />
                    {statuses.map(status => {
                        const ICON = ICONS[`validation_status_${status}`]
                        return <TableCell
                            key={status}
                        >
                            <Tooltip title={status} describeChild={true}>
                                <ICON color={get_color(status)} fontSize="large"/>
                            </Tooltip>
                        </TableCell>
                    })}
                </TableRow>
            </TableHead>
            <TableBody>
                {query.data && (query.data as SchemaValidationSummary[]).map((d: SchemaValidationSummary) => d.lookup_key)
                    .filter((k): k is LookupKey => k !== undefined)
                    .filter((lookupKey: LookupKey, i: number, self: LookupKey[]) => self.indexOf(lookupKey) === i)
                    .map((lookupKey: LookupKey) => <StatusSummary
                        key={lookupKey}
                        lookupKey={lookupKey}
                        data={query.data as SchemaValidationSummary[]}
                        statuses={statuses}
                    />)}
            </TableBody>
        </Table>
    </TableContainer>
}