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
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import React, {useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import {PATHS} from "../../App";
import Divider from "@mui/material/Divider";
import {Serializable, SerializableObject} from "./TypeChanger";
import {Family} from "./ResourceCard";

const deep_copy = (obj: any) => JSON.parse(JSON.stringify(obj))

type ResourceFamilyCardProps<T extends Family> = {
    uuid: string
    type: string
    child_type: keyof typeof PATHS & keyof typeof ICONS
    // Can't get a good type mask for generic API interface without a lot of work
    api: any
    path_key: keyof typeof PATHS
    editing?: boolean
    expanded?: boolean
    read_only_fields?: (keyof T)[]
}

/**
 * Return a string representation of a family object
 * @param data
 */
export function getFamilyRepresentation(data: Partial<Family>) {
    console.log("getFamilyRepresentation", data)
    if (Object.keys(data).includes("cells"))
        return `${data.manufacturer} ${data.model} (${data.form_factor} ${data.chemistry})`
    if (Object.keys(data).includes("equipment"))
        return `${data.manufacturer} ${data.model} (${data.type})`
    return `${data.identifier}`
}

export function type_to_api_type(type: string) {
    return type.replace(/s?_family/g, "Families")
}

export default function ResourceFamilyCard<T extends Family>(
    {
        uuid,
        type,
        child_type,
        api,
        read_only_fields,
        editing,
        path_key,
        expanded,
        ...cardProps
    }: ResourceFamilyCardProps<T> & CardProps
) {
    console.log("ResourceFamilyCard", {uuid, type, child_type, api, read_only_fields, editing, path_key, expanded, cardProps})

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
    const [data, _setData] =
        useState<T>()

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
        _setData(data)
    }

    const api_handler = new api()

    const api_type = type_to_api_type(type)

    console.log(api_type, api_handler[`${api_type}Retrieve`], api_handler[`${api_type}PartialUpdate`])

    const query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [`${api_type}_retrieve`, uuid],
        queryFn: () => api_handler[`${api_type}Retrieve`](uuid).then((r: AxiosResponse<T>) => {
            console.log(`${api_type}_retrieve ${uuid} response`, r)
            if (r === undefined) return Promise.reject("No data in response")
            splitData(r.data)
            return r
        })
    })

    // Mutations for saving edits
    const queryClient = useQueryClient()
    const update_mutation =
        useMutation<AxiosResponse<T>, AxiosError, SerializableObject>(
            (data: SerializableObject) => api_handler[`${api_type}PartialUpdate`](uuid, data),
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

    const representation = getFamilyRepresentation(data || {})

    const action = <CardActionBar
        type={type}
        uuid={uuid}
        path={PATHS[path_key]}
        highlight_count={data && data[child_type.toLowerCase()] instanceof Array?
            (data[child_type.toLowerCase()] as Serializable[]).length : 0}
        highlight_icon_key={child_type}
        highlight_path={`${PATHS[child_type]}?family=${uuid}`}
        highlight_tooltip={`View ${child_type} in this family`}
        editable={!!data?.permissions.write}
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

    const loadingBody = <Card key={uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS[path_key]}/${uuid}`}>{uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS[path_key]}>Cell</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent>
            <Grid container>
                <LoadingChip icon={<ICONS.FAMILY/>}/>
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>}/>
            </Grid>
        </CardContent> : <CardContent />}
    </Card>

    const cardBody = <Card key={uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICONS.FAMILY/></Avatar>}
            title={<A component={Link} to={`${PATHS[path_key]}/${uuid}`}>{representation}</A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS[path_key]}>Cell</A>
                <TeamChip url={data?.team!.toString() || ""} sx={{fontSize: "smaller"}}/>
            </Stack>}
            action={action}
        />
        {isExpanded? <CardContent sx={{maxHeight: isEditMode? "80vh" : "unset", overflowY: "auto"}}>
            <Stack spacing={1}>
                <Divider key="read-props-header">Read-only properties</Divider>
                {data && <PrettyObject
                    key="read-props"
                    target={readOnlyData}
                />}
                <Divider key="write-props-header">Editable properties</Divider>
                {data && <PrettyObject
                    key="write-props"
                    target={editableData}
                    edit_mode={isEditMode}
                    type_locked_keys={['identifier']}
                    onEdit={setEditableData}
                />}
            </Stack>
        </CardContent> : <CardContent />}
    </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.FAMILY/></Avatar>}
                title={uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS[path_key]}>
                        {(type.charAt(0).toUpperCase() + type.slice(1)).replace(/_/g, " ")}
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