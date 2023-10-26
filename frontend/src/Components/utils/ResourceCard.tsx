import {CardProps} from "@mui/material";
import CardActionBar from "../utils/CardActionBar";
import {id_from_ref_props} from "./misc";
import PrettyObject from "./PrettyObject";
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
import TeamChip from "../team/TeamChip";
import React, {useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import Divider from "@mui/material/Divider";
import {SerializableObject} from "./TypeChanger";
import {deep_copy} from "./misc";
import {
    API_HANDLERS, DISPLAY_NAMES,
    DISPLAY_NAMES_PLURAL,
    FAMILY_LOOKUP_KEYS,
    FILTER_NAMES,
    PATHS, ICONS, API_SLUGS, GET_REPRESENTATIONS
} from "../../constants";
import ResourceFamilyChip from "./ResourceFamilyChip";

export type Permissions = { read?: boolean, write?: boolean, create?: boolean, destroy?: boolean }
export type Family = { uuid: string, permissions: Permissions } & SerializableObject
export type Resource = { family: string, cycler_tests: string[], team: string } & Family

type ResourceCardProps<T extends Resource> = {
    uuid: string
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof DISPLAY_NAMES &
        keyof typeof DISPLAY_NAMES_PLURAL &
        keyof typeof FILTER_NAMES &
        keyof typeof FAMILY_LOOKUP_KEYS &
        keyof typeof API_HANDLERS
    editing?: boolean
    expanded?: boolean
    read_only_fields?: (keyof T)[]
}

export type AddProps<T> = T & {[key: string]: any}

export default function ResourceCard<T extends Resource, F extends Family>(
    {
        uuid,
        lookup_key,
        read_only_fields,
        editing,
        expanded,
        ...cardProps
    }: ResourceCardProps<T> & CardProps
) {
    console.log("ResourceCard", {uuid: uuid, lookup_key: lookup_key, read_only_fields, editing, expanded, cardProps})
    const family_key = FAMILY_LOOKUP_KEYS[lookup_key]

    const { classes } = useStyles();
    const [isEditMode, _setIsEditMode] = useState<boolean>(editing || false)
    const [isExpanded, setIsExpanded] = useState<boolean>(expanded || isEditMode)
    const [editableData, _setEditableData] =
        useState<SerializableObject>({})
    const [editableDataHistory, setEditableDataHistory] =
        useState<SerializableObject[]>([])
    const [editableDataHistoryIndex, setEditableDataHistoryIndex] =
        useState<number>(0)
    const [readOnlyData, _setReadOnlyData] =
        useState<Partial<T>>({})
    const [target_data, _setTargetData] =
        useState<T>()
    const [family, _setFamily] =
        useState<string>()
    const [family_data, setFamilyData] =
        useState<F>()

    const setEditableData = (d: SerializableObject) => {
        console.log("setEditableData", d)
        const _d = deep_copy(d)  // can be used for both history and value because value is always updated deeply
        _setEditableData(_d)
        setEditableDataHistoryIndex(editableDataHistoryIndex + 1)
        setEditableDataHistory([
            ...editableDataHistory.slice(0, editableDataHistoryIndex + 1),
            _d
        ])
    }
    const undoEditableData = () => {
        if (editableDataHistoryIndex > 0) {
            const index = editableDataHistoryIndex - 1
            _setEditableData(editableDataHistory[index])
            setEditableDataHistoryIndex(index)
        }
    }
    const redoEditableData = () => {
        if (editableDataHistoryIndex < editableDataHistory.length - 1) {
            const index = editableDataHistoryIndex + 1
            _setEditableData(editableDataHistory[index])
            setEditableDataHistoryIndex(index)
        }
    }
    const setEditing = (e: boolean) => {
        _setIsEditMode(e)
        if (e) setIsExpanded(e)
    }
    const splitData = (data: T) => {
        console.log("Splitting data", data)
        const read_only_data: Partial<T> = {}
        const write_data: SerializableObject = {}
        const _read_only_fields = read_only_fields || []
        for (const k of Object.keys(data)) {
            if (_read_only_fields.includes(k as keyof T)) {
                read_only_data[k as keyof T] = data[k] as T[keyof T]
            } else {
                write_data[k as keyof SerializableObject] = data[k]
            }
        }
        _setEditableData(write_data)
        setEditableDataHistory([write_data])
        setEditableDataHistoryIndex(0)
        _setReadOnlyData(read_only_data)
        _setTargetData(data)
        _setFamily(id_from_ref_props<string>(data.family))
    }

    const target_api_handler = new API_HANDLERS[lookup_key]()
    const target_get = target_api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof target_api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const target_patch = target_api_handler[
        `${API_SLUGS[lookup_key]}PartialUpdate` as keyof typeof target_api_handler
        ] as (uuid: string, data: SerializableObject) => Promise<AxiosResponse<T>>
    const family_api_handler = new API_HANDLERS[family_key]()
    const family_get = family_api_handler[
        `${API_SLUGS[family_key]}Retrieve` as keyof typeof family_api_handler
        ] as (uuid: string) => Promise<AxiosResponse<F>>

    const target_query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, uuid],
        queryFn: () => target_get(uuid).then((r: AxiosResponse<T>) => {
            console.log(lookup_key, 'retrieve', uuid, r)
            if (r === undefined) return Promise.reject("No data in response")
            splitData(r.data)
            return r
        })
    })
    const family_query = useQuery<AxiosResponse<F>, AxiosError>({
        queryKey: [family_key, family || "should_not_be_called"],
        queryFn: () => family_get(id_from_ref_props<string>(target_query.data!.data.family))
            .then((r: AxiosResponse<F>) => {
                console.log(family_key, 'get', id_from_ref_props<string>(target_query.data!.data.family), r)
                if (r === undefined) return Promise.reject("No data in response")
                setFamilyData(r.data)
                return r
            }),
        enabled: !!family
    })

    // Mutations for saving edits
    const queryClient = useQueryClient()
    const update_mutation =
        useMutation<AxiosResponse<T>, AxiosError, SerializableObject>(
            (data: SerializableObject) => target_patch(uuid, data),
            {
                onSuccess: (data, variables, context) => {
                    if (data === undefined) {
                        console.warn("No data in mutation response", {data, variables, context})
                        return
                    }
                    queryClient.setQueryData(['cell_retrieve', uuid], data)
                },
                onError: (error, variables, context) => {
                    console.error(error)
                },
            })

    const action = <CardActionBar
        lookup_key={lookup_key}
        uuid={uuid}
        family_uuid={target_data?.family? id_from_ref_props<string>(target_data?.family) : undefined}
        highlight_count={target_data?.cycler_tests.length}
        highlight_lookup_key="CYCLER_TEST"
        editable={!!target_data?.permissions.write}
        editing={isEditMode}
        setEditing={setEditing}
        onUndo={undoEditableData}
        onRedo={redoEditableData}
        undoable={editableDataHistoryIndex > 0}
        redoable={editableDataHistoryIndex < editableDataHistory.length - 1}
        onEditSave={() => {
            update_mutation.mutate(editableData)
            return true
        }}
        onEditDiscard={() => {
            if (editableDataHistoryIndex && !window.confirm("Discard all changes?"))
                return false
            _setEditableData({...editableData, ...editableDataHistory[0]})
            setEditableDataHistory([editableDataHistory[0]])
            setEditableDataHistoryIndex(0)
            return true
        }}
        expanded={isExpanded}
        setExpanded={setIsExpanded}
    />

    const ICON = ICONS[lookup_key]
    const FAMILY_ICON = ICONS[family_key]

    const loadingBody = <Card key={uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${uuid}`}>{uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                <LoadingChip icon={<ICONS.TEAM/>} />
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent>
            <Grid container>
                <LoadingChip icon={<FAMILY_ICON/>}/>
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TEST/>}/>
            </Grid>
        </CardContent> : <CardContent />}
    </Card>

    const cardBody = <Card key={uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICON /></Avatar>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${uuid}`}>
                <>
                    {GET_REPRESENTATIONS[family_key](family_data)} {target_data?.identifier ?? uuid}
                </>
            </A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                <TeamChip url={target_data?.team!} sx={{fontSize: "smaller"}}/>
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent sx={{maxHeight: isEditMode? "80vh" : "unset", overflowY: "auto"}}>
            <Stack spacing={1}>
                <Divider key="read-props-header">Read-only properties</Divider>
                {target_data && <PrettyObject
                    key="read-props"
                    target={readOnlyData}
                />}
                <Divider key="write-props-header">Editable properties</Divider>
                {target_data && <PrettyObject
                    key="write-props"
                    target={editableData}
                    edit_mode={isEditMode}
                    type_locked_keys={['identifier']}
                    onEdit={setEditableData}
                />}
                {family_data?.uuid && <Divider key="family-props-header">
                    Inherited from
                    <ResourceFamilyChip
                        uuid={family_data?.uuid}
                        lookup_key={family_key}
                    />
                </Divider>}
                {family_data && <PrettyObject
                    target={family_data}
                    exclude_keys={[...Object.keys(target_data!), 'cells']}
                />}
            </Stack>
        </CardContent> : <CardContent />}
    </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICON /></Avatar>}
                title={uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                </Stack>}
            />
        }
    />

    return <QueryWrapper
        queries={[target_query, family_query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}