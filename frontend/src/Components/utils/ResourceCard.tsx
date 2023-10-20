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
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import React, {CElement, useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosRequestConfig, AxiosResponse} from "axios";
import {PATHS} from "../../App";
import Divider from "@mui/material/Divider";
import {SerializableObject} from "./TypeChanger";
import {BaseAPI} from "../../api_codegen/base";

const deep_copy = (obj: any) => JSON.parse(JSON.stringify(obj))

type Permissions = { read?: boolean, write?: boolean, create?: boolean, destroy?: boolean }
type Family = { uuid: string, permissions: Permissions } & SerializableObject
type Resource = { family: string, cycler_tests: string[], team: string } & Family

type ResourceCardProps<T extends Resource> = {
    target_uuid: string
    target_type: string
    target_api: typeof BaseAPI
    family_api: typeof BaseAPI
    FamilyChip: (props: any) => CElement<any, any>
    path_key: keyof typeof PATHS
    editing?: boolean
    expanded?: boolean
    read_only_fields?: (keyof T)[]
}

export type AddProps<T> = T & {[key: string]: any}

export default function ResourceCard<T extends Resource, F extends Family>(
    {
        target_uuid,
        target_type,
        target_api,
        family_api,
        FamilyChip,
        read_only_fields,
        editing,
        path_key,
        expanded,
        ...cardProps
    }: ResourceCardProps<T> & CardProps
) {
    console.log("ResourceCard", {target_uuid, target_type, target_api, family_api, FamilyChip, read_only_fields, editing, path_key, expanded, cardProps})

    const { classes } = useStyles();
    const [isEditMode, _setIsEditMode] = useState<boolean>(editing || true)
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

    const target_api_handler = new target_api() as any
    const family_api_handler = new family_api() as any

    const target_query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [`${target_type}_retrieve`, target_uuid],
        queryFn: () => target_api_handler[`${target_type}Retrieve`](target_uuid).then((r: AxiosResponse<T>) => {
            console.log(`${target_type}_retrieve ${target_uuid} response`, r)
            if (r === undefined) return Promise.reject("No data in response")
            splitData(r.data)
            return r
        })
    })
    const family_query = useQuery<AxiosResponse<F>, AxiosError>({
        queryKey: [`${target_type}_family_retrieve`, family || "should_not_be_called"],
        queryFn: () => family_api_handler[`${target_type}FamiliesRetrieve`](id_from_ref_props<string>(target_query.data!.data.family))
            .then((r: AxiosResponse<F>) => {
                console.log(`${target_type}_family_retrieve ${id_from_ref_props<string>(target_query.data!.data.family)} response`, r)
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
        (data: SerializableObject) => target_api_handler[`${target_type}PartialUpdate`](target_uuid, data),
        {
            onSuccess: (data, variables, context) => {
                if (data === undefined) {
                    console.warn("No data in mutation response", {data, variables, context})
                    return
                }
                queryClient.setQueryData(['cell_retrieve', target_uuid], data)
            },
            onError: (error, variables, context) => {
                console.error(error)
            },
        })

    const action = <CardActionBar
        type={target_type}
        uuid={target_uuid}
        path={PATHS[path_key]}
        family_uuid={target_data?.family!}
        cycler_test_count={target_data?.cycler_tests.length}
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

    const loadingBody = <Card key={target_uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS[path_key]}/${target_uuid}`}>{target_uuid}</A>}
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

    const cardBody = <Card key={target_uuid} className={clsx(classes.item_card)} {...cardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
            title={<A component={Link} to={`${PATHS[path_key]}/${target_uuid}`}>
                {`${family_data?.manufacturer} ${family_data?.model} ${target_data?.identifier}`}
            </A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS[path_key]}>Cell</A>
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
                    Inherited from <FamilyChip uuid={family_data?.uuid}/>
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
                avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
                title={target_uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS[path_key]}>
                        {target_type.charAt(0).toUpperCase() + target_type.slice(1)}
                    </A>
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