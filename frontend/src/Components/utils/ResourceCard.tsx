import CardActionBar from "../utils/CardActionBar";
import {deep_copy, id_from_ref_props} from "./misc";
import PrettyObject, {PrettyObjectFromQuery} from "./PrettyObject";
import useStyles from "../../UseStyles";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import Card, {CardProps} from "@mui/material/Card";
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
import React, {Fragment, ReactNode, useContext, useEffect, useRef, useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import Divider from "@mui/material/Divider";
import {Serializable, SerializableObject} from "./TypeChanger";
import {
    API_HANDLERS,
    API_SLUGS,
    CHILD_LOOKUP_KEYS,
    CHILD_PROPERTY_NAMES,
    DISPLAY_NAMES,
    FAMILY_LOOKUP_KEYS,
    FIELDS,
    ICONS, is_lookup_key,
    PATHS, PRIORITY_LEVELS, LookupKey
} from "../../constants";
import ResourceChip from "./ResourceChip";
import ErrorBoundary from "./ErrorBoundary";
import UndoRedoProvider, {UndoRedoContext} from "./UndoRedoContext";
import Representation from "./Representation";
import {FILTER_MODES, FilterContext} from "../filtering/FilterContext";

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

export type ResourceCardProps = {
    resource_id: string|number
    lookup_key: LookupKey
    editing?: boolean
    expanded?: boolean
}

function ResourceCard<T extends BaseResource>(
    {
        resource_id,
        lookup_key,
        editing,
        expanded,
        ...cardProps
    }: ResourceCardProps & CardProps
) {
    // console.log("ResourceCard", {uuid: uuid, lookup_key: lookup_key, read_only_fields, editing, expanded, cardProps})

    const { classes } = useStyles();
    const [isEditMode, _setIsEditMode] = useState<boolean>(editing || false)
    const [isExpanded, setIsExpanded] = useState<boolean>(expanded || isEditMode)

    const {activeFilters} = useContext(FilterContext)

    // useContext is wrapped in useRef because we update the context in our useEffect API data hook
    const UndoRedo = useContext(UndoRedoContext)
    const UndoRedoRef = useRef(UndoRedo)

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
            UndoRedoRef.current.set(data)
        }
    }, [query.data, lookup_key]);

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
                    console.error(error, {variables, context})
                },
            })

    // Type guards for family and children
    const get_has_family = (key: string|number): key is keyof typeof FAMILY_LOOKUP_KEYS =>
        Object.keys(FAMILY_LOOKUP_KEYS).includes(key as string)
    const has_family = get_has_family(lookup_key)
    const get_is_family = (key: string|number): key is keyof typeof CHILD_PROPERTY_NAMES =>
        Object.keys(CHILD_PROPERTY_NAMES).includes(key as string)
    const is_family = get_is_family(lookup_key)

    const family_key = has_family? FAMILY_LOOKUP_KEYS[lookup_key] : undefined
    const children: string[] = is_family? query.data?.data[CHILD_PROPERTY_NAMES[lookup_key]] as string[] : []

    const is_ct_resource = Object.keys(FIELDS[lookup_key]).includes("cycler_tests")

    const ICON = ICONS[lookup_key]
    const FAMILY_ICON = family_key? ICONS[family_key] : undefined

    // The card action bar controls the expanded state and editing state
    const action = <CardActionBar
        lookup_key={lookup_key}
        resource_id={resource_id}
        family_uuid={query.data?.data.family? id_from_ref_props<string>(query.data?.data.family) : undefined}
        highlight_count={query.data?.data.cycler_tests?.length ?? children?.length}
        highlight_lookup_key={
            is_ct_resource? "CYCLER_TEST" :
                is_family? CHILD_LOOKUP_KEYS[lookup_key] : undefined
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

    const cardBody = <CardContent sx={{
        maxHeight: isEditMode? "80vh" : "unset",
        overflowY: "auto",
        "& li": isEditMode? {marginTop: (t) => t.spacing(0.5)} : undefined,
        "& table": isEditMode? {borderCollapse: "separate", borderSpacing: (t) => t.spacing(0.5)} :
            undefined,
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
            {UndoRedo.current && <PrettyObject
                key="write-props"
                target={UndoRedo.current}
                edit_mode={isEditMode}
                lookup_key={lookup_key}
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
                filter={(d, lookup_key) => {
                    const data = deep_copy(d)
                    if (get_is_family(lookup_key))
                        delete data[CHILD_PROPERTY_NAMES[lookup_key]]
                    return data
                }}
            />}
        </Stack>
    </CardContent>

    const is_family_child = (child_key: LookupKey, family_key: LookupKey) => {
        if (!get_is_family(family_key)) return false
        if (!get_has_family(child_key)) return false
        return CHILD_LOOKUP_KEYS[family_key] === child_key
    }

    const summarise = (
        data: Serializable,
        many: boolean,
        key: string,
        lookup?: LookupKey
    ): ReactNode => {
        if (many)
            return <Grid container>{data instanceof Array ?
                data.map((d, i) => <Grid key={i}>{summarise(d, false, key, lookup)}</Grid>) :
                <Grid>{summarise(data, false, key, lookup)}</Grid>
            }</Grid>

        return lookup && is_lookup_key(lookup)?
            <ResourceChip
                resource_id={id_from_ref_props<string>(data as string|number)}
                lookup_key={lookup}
                short_name={is_family_child(lookup, lookup_key)}
            /> : <>`${key}: ${data}`</>
    }

    const cardSummary = <CardContent>
        {query.data && <Grid container spacing={1}>{
            Object.entries(FIELDS[lookup_key])
                .filter(([_, v]) => v.priority === PRIORITY_LEVELS.SUMMARY)
                .map(([k, v]) => <Grid key={k}>{summarise(query.data.data[k], v.many, k, v.type)}</Grid>)
        }</Grid>}
    </CardContent>

    const filter_mode = activeFilters[lookup_key].mode === FILTER_MODES.ANY? "some" : "every"
    const passes_filters = activeFilters[lookup_key].filters.length === 0 ||
        activeFilters[lookup_key].filters[filter_mode](f => f.family.fun(query.data?.data[f.key], f.test_versus))

    const cardContent = !passes_filters? <Fragment key={resource_id} /> :
        <Card key={resource_id} className={clsx(classes.item_card)} {...cardProps}>
            <CardHeader
                avatar={<Avatar variant="square"><ICON /></Avatar>}
                title={<A component={Link} to={`${PATHS[lookup_key]}/${resource_id}`}>
                    <Representation
                        resource_id={resource_id}
                        lookup_key={lookup_key}
                        prefix={family_key && query.data?.data.family ?
                            <Representation
                                resource_id={id_from_ref_props<string>(query.data?.data.family)}
                                lookup_key={family_key}
                                suffix=" "
                            /> : undefined}
                    />
                </A>}
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
            {isExpanded? cardBody : cardSummary}
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
        success={cardContent}
    />
}

export default function WrappedResourceCard<T extends BaseResource>(props: ResourceCardProps & CardProps) {
    return <UndoRedoProvider>
        <ErrorBoundary
            fallback={(error: Error) => <ErrorCard
                message={error.message}
                header={
                    <CardHeader
                        avatar={<Avatar variant="square">E</Avatar>}
                        title="Error"
                        subheader={`Error with ResourceCard for 
                        ${props.lookup_key} ${props.resource_id} [editing=${props.editing}]`
                        }
                    />
                }
            />}
        >
            <ResourceCard<T> {...props} />
        </ErrorBoundary>
    </UndoRedoProvider>
}