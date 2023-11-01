import {CardProps} from "@mui/material";
import CardActionBar from "../utils/CardActionBar";
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
import React, {useEffect, useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import Divider from "@mui/material/Divider";
import {Serializable, SerializableObject} from "./TypeChanger";
import ChildCard, {Family} from "./ChildCard";
import {deep_copy, id_from_ref_props} from "./misc";
import {
    API_HANDLERS, API_SLUGS,
    CHILD_LOOKUP_KEYS,
    CHILD_PROPERTY_NAMES, DISPLAY_NAMES, FIELDS,
    GET_REPRESENTATIONS,
    ICONS,
    PATHS
} from "../../constants";
import ResourceChip from "./ResourceChip";

type ResourceFamilyCardProps<T extends Family> = {
    family_id: string
    lookup_key: keyof typeof ICONS &
        keyof typeof PATHS &
        keyof typeof CHILD_LOOKUP_KEYS
    editing?: boolean
    expanded?: boolean
    read_only_fields?: (keyof T)[]
}

export default function FamilyCard<T extends Family>(
    {
        family_id,
        lookup_key,
        editing,
        expanded,
        ...cardProps
    }: ResourceFamilyCardProps<T> & CardProps
) {
    console.log("ResourceFamilyCard", {family_id: family_id, lookup_key, editing, expanded, cardProps})

    const child_key = CHILD_LOOKUP_KEYS[lookup_key]
    const ICON = ICONS[lookup_key]
    const { classes } = useStyles();

    const [isEditMode, _setIsEditMode] = useState<boolean>(editing || false)
    const [isExpanded, setIsExpanded] = useState<boolean>(expanded || isEditMode)

    // TODO: refactor edit history stuff into a hook/context/reducer
    const [editableData, _setEditableData] =
        useState<SerializableObject>({})
    const [editableDataHistory, setEditableDataHistory] =
        useState<SerializableObject[]>([])
    const [editableDataHistoryIndex, setEditableDataHistoryIndex] =
        useState<number>(0)
    const [readOnlyData, _setReadOnlyData] =
        useState<Partial<T>>({})

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
        const _read_only_fields = Object.entries(FIELDS[lookup_key])
            .filter(([k, v]) => v.readonly)
            .map(([k, v]) => k as keyof T)
        for (const k of Object.keys(data)) {
            const kk = k as keyof T
            if (_read_only_fields.includes(kk)) {
                read_only_data[kk] = data[k] as T[keyof T]
            } else {
                write_data[k as keyof SerializableObject] = data[k]
            }
        }
        _setEditableData(write_data)
        setEditableDataHistory([write_data])
        setEditableDataHistoryIndex(0)
        _setReadOnlyData(read_only_data)
    }

    const api_handler = new API_HANDLERS[lookup_key]()
    const api_get = api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>
    const api_patch = api_handler[
        `${API_SLUGS[lookup_key]}PartialUpdate` as keyof typeof api_handler
        ] as (uuid: string, data: SerializableObject) => Promise<AxiosResponse<T>>

    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, family_id],
        queryFn: () => api_get.bind(api_handler)(family_id)
    })

    useEffect(() => {
        if (query.data?.data) splitData(query.data.data)
    }, [query.data?.data]);

    // Mutations for saving edits
    const queryClient = useQueryClient()
    const update_mutation =
        useMutation<AxiosResponse<T>, AxiosError, SerializableObject>(
            (data: SerializableObject) => api_patch.bind(api_handler)(family_id, data),
            {
                onSuccess: (data, variables, context) => {
                    if (data === undefined) {
                        console.warn("No data in mutation response", {data, variables, context})
                        return
                    }
                    queryClient.setQueryData(['cell_retrieve', family_id], data)
                },
                onError: (error, variables, context) => {
                    console.error(error)
                },
            })

    const action = <CardActionBar
        lookup_key={lookup_key}
        uuid={family_id}
        highlight_count={query.data && query.data.data[CHILD_PROPERTY_NAMES[lookup_key]] instanceof Array?
            (query.data.data[CHILD_PROPERTY_NAMES[lookup_key]] as Serializable[]).length : 0}
        highlight_lookup_key={child_key}
        editable={!!query.data?.data.permissions.write}
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

    const loadingBody = <Card key={family_id} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${family_id}`}>{family_id}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                <LoadingChip icon={<ICONS.TEAM/>} />
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent>
            <Grid container>
                <LoadingChip icon={<ICON/>}/>
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TEST/>}/>
            </Grid>
        </CardContent> : <CardContent />}
    </Card>

    const cardBody = <Card key={family_id} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICON/></Avatar>}
            title={<A component={Link} to={`${PATHS[lookup_key]}/${family_id}`}>
                {GET_REPRESENTATIONS[lookup_key](query.data?.data)}
            </A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS[lookup_key]}>{DISPLAY_NAMES[lookup_key]}</A>
                {query.data && <ResourceChip
                    lookup_key="TEAM"
                    resource_id={id_from_ref_props<number>(query.data.data.team)}
                    sx={{fontSize: "smaller"}}
                />}
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent sx={{maxHeight: isEditMode? "80vh" : "unset", overflowY: "auto"}}>
            <Stack spacing={1}>
                <Divider key="read-props-header">Read-only properties</Divider>
                {query.data && <PrettyObject
                    key="read-props"
                    target={readOnlyData}
                />}
                <Divider key="write-props-header">Editable properties</Divider>
                {query.data && <PrettyObject
                    key="write-props"
                    target={editableData}
                    edit_mode={isEditMode}
                    type_locked_keys={['identifier']}
                    onEdit={setEditableData}
                />}
                <Divider key="child-cards-header">Instances</Divider>
                {query.data?.data[CHILD_PROPERTY_NAMES[lookup_key]]?.map((child: string) => <ChildCard
                    resource_id={id_from_ref_props(child)} lookup_key={CHILD_LOOKUP_KEYS[lookup_key]} />)}
            </Stack>
        </CardContent> : <CardContent />}
    </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICON/></Avatar>}
                title={family_id}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS[lookup_key]}>
                        {(lookup_key.charAt(0).toUpperCase() + lookup_key.slice(1)).replace(/_/g, " ")}
                    </A>
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