import {CardProps} from "@mui/material";
import CardActionBar from "../utils/CardActionBar";
import {deep_copy, id_from_ref_props} from "./misc";
import PrettyObject, {PrettyObjectFromQuery, PrettyObjectProps} from "./PrettyObject";
import useStyles from "../../UseStyles";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import Card from "@mui/material/Card";
import {Link} from "react-router-dom";
import clsx from "clsx";
import CardHeader from "@mui/material/CardHeader";
import CircularProgress from "@mui/material/CircularProgress";
import A from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import LoadingChip from "./LoadingChip";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import React, {useContext, useEffect, useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import Divider from "@mui/material/Divider";
import {SerializableObject} from "./TypeChanger";
import {
    API_HANDLERS,
    API_SLUGS,
    CHILD_LOOKUP_KEYS,
    CHILD_PROPERTY_NAMES,
    DISPLAY_NAMES,
    DISPLAY_NAMES_PLURAL,
    FAMILY_LOOKUP_KEYS,
    FIELDS,
    FILTER_NAMES,
    ICONS,
    PATHS
} from "../../constants";
import ResourceChip from "./ResourceChip";
import ErrorBoundary from "./ErrorBoundary";
import UndoRedoProvider, {UndoRedoContext} from "./UndoRedoContext";
import Representation from "./Representation";

export type Permissions = { read?: boolean, write?: boolean, create?: boolean, destroy?: boolean }
type child_keys = "cells"|"equipment"|"schedules"
export type BaseResource = ({uuid: string} | {id: number}) & {
    permissions: Permissions,
    team?: string,
    family?: string,
    cycler_tests?: string[],
} & {[key in child_keys]?: string[]} & SerializableObject
export type Family = BaseResource & ({cells: string[]} | {equipment: string[]} | {schedules: string[]})
export type Resource = { family: string, cycler_tests: string[] } & BaseResource

export type ResourceCardProps<T extends BaseResource> = {
    resource_id: string|number
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof DISPLAY_NAMES &
        keyof typeof DISPLAY_NAMES_PLURAL &
        keyof typeof FILTER_NAMES &
        keyof typeof API_HANDLERS
    editing?: boolean
    expanded?: boolean
}

export type AddProps<T> = T & {[key: string]: any}

function ResourceCard<T extends BaseResource>(
    {
        resource_id,
        lookup_key,
        editing,
        expanded,
        ...cardProps
    }: ResourceCardProps<T> & CardProps
) {
    // console.log("ResourceCard", {uuid: uuid, lookup_key: lookup_key, read_only_fields, editing, expanded, cardProps})

    const { classes } = useStyles();
    const [isEditMode, _setIsEditMode] = useState<boolean>(editing || false)
    const [isExpanded, setIsExpanded] = useState<boolean>(expanded || isEditMode)

    const UndoRedo = useContext(UndoRedoContext)

    const setEditing = (e: boolean) => {
        _setIsEditMode(e)
        if (e) setIsExpanded(e)
    }

    const api_handler = new API_HANDLERS[lookup_key]()
    const get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const patch = api_handler[
        `${API_SLUGS[lookup_key]}PartialUpdate` as keyof typeof api_handler
        ] as (uuid: string, data: SerializableObject) => Promise<AxiosResponse<T>>

    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, resource_id],
        queryFn: () => get.bind(api_handler)(String(resource_id))
    })

    useEffect(() => {
        if (query.data) {
            const data = deep_copy(query.data.data)
            Object.entries(FIELDS[lookup_key]).forEach(([k, v]) => {
                if (v.readonly) {
                    delete data[k]
                }
            })
            UndoRedo.set(data)
        }
    }, [query.data]);

    // Mutations for saving edits
    const queryClient = useQueryClient()
    const update_mutation =
        useMutation<AxiosResponse<T>, AxiosError, SerializableObject>(
            (data: SerializableObject) => patch.bind(api_handler)(String(resource_id), data),
            {
                onSuccess: (data, variables, context) => {
                    if (data === undefined) {
                        console.warn("No data in mutation response", {data, variables, context})
                        return
                    }
                    queryClient.setQueryData([lookup_key, resource_id], data)
                },
                onError: (error, variables, context) => {
                    console.error(error)
                },
            })

    const has_family = Object.keys(FAMILY_LOOKUP_KEYS).includes(lookup_key)
    const family_key = has_family?
        FAMILY_LOOKUP_KEYS[lookup_key as keyof typeof FAMILY_LOOKUP_KEYS] : undefined
    const is_family = Object.keys(CHILD_PROPERTY_NAMES).includes(lookup_key)
    const children: string[] = is_family?
        query.data?.data[CHILD_PROPERTY_NAMES[lookup_key as keyof typeof CHILD_PROPERTY_NAMES]] as string[] : []

    const is_ct_resource = Object.keys(FIELDS[lookup_key as keyof typeof FIELDS]).includes("cycler_tests")

    const ICON = ICONS[lookup_key]
    const FAMILY_ICON = family_key? ICONS[family_key] : undefined

    // The card action bar controls the expanded state and editing state
    const action = <CardActionBar
        lookup_key={lookup_key}
        resource_id={resource_id}
        family_uuid={query.data?.data.family? id_from_ref_props<string>(query.data?.data.family) : undefined}
        highlight_count={query.data?.data.cycler_tests?.length ?? children.length}
        highlight_lookup_key={
            is_ct_resource? "CYCLER_TEST" :
                is_family? CHILD_LOOKUP_KEYS[lookup_key as keyof typeof CHILD_LOOKUP_KEYS] :
                    undefined
        }
        editable={!!query.data?.data.permissions.write}
        editing={isEditMode}
        setEditing={setEditing}
        onUndo={UndoRedo.undo}
        onRedo={UndoRedo.redo}
        undoable={UndoRedo.can_undo}
        redoable={UndoRedo.can_redo}
        onEditSave={() => {
            update_mutation.mutate(UndoRedo.current)
            return true
        }}
        onEditDiscard={() => {
            if (UndoRedo.can_undo && !window.confirm("Discard all changes?"))
                return false
            UndoRedo.reset()
            return true
        }}
        expanded={isExpanded}
        setExpanded={setIsExpanded}
    />

    const loadingBody = <Card key={resource_id} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${resource_id}`}>{resource_id}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                <LoadingChip icon={<ICONS.TEAM/>} />
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent>
            {FAMILY_ICON !== undefined && <Grid container>
                <LoadingChip icon={<FAMILY_ICON/>}/>
            </Grid>}
            {is_ct_resource && <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TEST/>}/>
            </Grid>}
        </CardContent> : <CardContent />}
    </Card>

    const cardBody = <Card key={resource_id} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICON /></Avatar>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${resource_id}`}>{
                query.data?
                    (has_family && family_key && query.data.data.family)? <>
                            <Representation resource_id={id_from_ref_props<string>(query.data.data.family)} lookup_key={family_key}/>
                            {" "}
                            <Representation resource_id={resource_id} lookup_key={lookup_key} />
                        </> :
                        <Representation resource_id={resource_id} lookup_key={lookup_key} /> :
                    resource_id
            }</A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                {query.data?.data.team !== undefined && <ResourceChip
                    lookup_key="TEAM"
                    resource_id={id_from_ref_props<number>(query.data.data.team)}
                    sx={{fontSize: "smaller"}}
                />}
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent sx={{
            maxHeight: isEditMode? "80vh" : "unset",
            overflowY: "auto",
            "& li": isEditMode? {marginTop: (t) => t.spacing(0.5)} : undefined,
            "& table": isEditMode? {borderCollapse: "separate", borderSpacing: (t) => t.spacing(0.5)} : undefined,
        }}>
            <Stack spacing={1}>
                <Divider key="read-props-header">Read-only properties</Divider>
                {query.data && <PrettyObjectFromQuery
                    resource_id={resource_id}
                    lookup_key={lookup_key}
                    key="read-props"
                    filter={(d, lookup_key) => {
                        const data = deep_copy(d)
                        // Unrecognised fields are always editable
                        Object.keys(data).forEach(k => {
                            if (!Object.keys(FIELDS[lookup_key]).includes(k))
                                delete data[k]
                        })
                        Object.entries(FIELDS[lookup_key]).forEach(([k, v]) => {
                            if (!v.readonly)
                                delete data[k]
                        })
                        return data
                    }}
                />}
                <Divider key="write-props-header">Editable properties</Divider>
                {query.data && <PrettyObject
                    key="write-props"
                    target={UndoRedo.current}
                    edit_mode={isEditMode}
                    type_locked_keys={['identifier']}
                    onEdit={UndoRedo.update}
                />}
                {has_family && <Divider key="family-props-header">
                    Inherited from
                    {query.data?.data.family?
                        <ResourceChip
                            resource_id={id_from_ref_props<string>(query.data?.data.family)}
                            lookup_key={family_key!}
                        /> : FAMILY_ICON && <LoadingChip icon={<FAMILY_ICON/>}/> }
                </Divider>}
                {query.data?.data.family && family_key && <PrettyObjectFromQuery
                    resource_id={id_from_ref_props<string>(query.data?.data.family)}
                    lookup_key={family_key}
                    exclude_keys={query.data? [...Object.keys(query.data), CHILD_PROPERTY_NAMES[family_key]] : []}
                />}
            </Stack>
        </CardContent> : <CardContent />}
    </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICON /></Avatar>}
                title={resource_id}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                </Stack>}
            />
        }
    />

    return <QueryWrapper
        queries={[query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}

export default function WrappedResourceCard<T extends BaseResource>(props: ResourceCardProps<T> & CardProps) {
    return <UndoRedoProvider>
        <ErrorBoundary
            fallback={(error: Error) => <ErrorCard
                message={error.message}
                header={
                    <CardHeader
                        avatar={<Avatar variant="square">E</Avatar>}
                        title="Error"
                        subheader={`Error with ResourceCard for ${props.lookup_key} ${props.resource_id} [editing=${props.editing}]`}
                    />
                }
            />}
        >
            <ResourceCard {...props} />
        </ErrorBoundary>
    </UndoRedoProvider>
}