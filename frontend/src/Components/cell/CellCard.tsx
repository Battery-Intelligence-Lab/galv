import {CardProps} from "@mui/material";
import CardActionBar from "../utils/CardActionBar";
import {ExpandableCardProps, id_from_ref_props} from "../utils/misc";
import PrettyObject from "../utils/PrettyObject";
import useStyles from "../../UseStyles";
import {Cell, CellFamiliesApi, CellFamily, CellsApi, PatchedCell} from "../../api_codegen";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import Card from "@mui/material/Card";
import {Link} from "react-router-dom";
import clsx from "clsx";
import CardHeader from "@mui/material/CardHeader";
import CircularProgress from "@mui/material/CircularProgress";
import A from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import LoadingChip from "../utils/LoadingChip";
import {ICONS} from "../../icons";
import CardContent from "@mui/material/CardContent";
import Grid from "@mui/material/Unstable_Grid2";
import Avatar from "@mui/material/Avatar";
import TeamChip from "../team/TeamChip";
import React, {useState} from "react";
import ErrorCard from "../error/ErrorCard";
import QueryWrapper, {QueryDependentElement} from "../utils/QueryWrapper";
import {AxiosError, AxiosResponse} from "axios";
import CellFamilyChip from "./CellFamilyChip";
import {PATHS} from "../../App";
import Divider from "@mui/material/Divider";

const deepcopy = (obj: any) => JSON.parse(JSON.stringify(obj))

export type AddProps<T> = T & {[key: string]: any}

export default function CellCard(props: ExpandableCardProps & CardProps) {
    // No nice way to do this automatically because TS is compile-time and the OpenAPI spec lists all fields in Patched* anyway
    const read_only_fields: (keyof Cell)[] = ['url', 'uuid', 'family', 'cycler_tests', 'permissions', 'in_use', 'team']

    const { classes } = useStyles();
    const [editing, _setEditing] = useState<boolean>(props.editing || true)
    const [expanded, setExpanded] = useState<boolean>(props.expanded || editing)
    const [editableData, _setEditableData] =
        useState<Partial<AddProps<PatchedCell>>>({})
    const [editableDataHistory, setEditableDataHistory] = useState<Partial<AddProps<PatchedCell>>[]>([])
    const [editableDataHistoryIndex, setEditableDataHistoryIndex] = useState<number>(0)
    const [readOnlyData, _setReadOnlyData] = useState<Partial<AddProps<Cell>>>({})

    const setEditing = (e: boolean) => {
        _setEditing(e)
        if (e) setExpanded(e)
    }

    const splitData = (data: AddProps<Cell>) => {
        console.log("Splitting data", data)
        const read_only_data: Partial<Cell> = {}
        const write_data: Partial<AddProps<PatchedCell>> = {}
        for (const k of Object.keys(data)) {
            if (read_only_fields.includes(k as keyof Cell)) {
                read_only_data[k as keyof Cell] = data[k]
            } else {
                write_data[k] = data[k]
            }
        }
        _setEditableData(write_data)
        setEditableDataHistory([write_data])
        setEditableDataHistoryIndex(0)
        _setReadOnlyData(read_only_data)
        _setCellData(data)
        _setFamily(id_from_ref_props<string>(data.family))
    }

    const setEditableData = (d: Partial<AddProps<PatchedCell>>) => {
        console.log("setEditableData", d)
        const _d = deepcopy(d)  // can be used for both history and value because value is always updated deeply
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
    const [cell_data, _setCellData] = useState<AddProps<Cell>>()
    const [family, _setFamily] = useState<string>()
    const [family_data, setFamilyData] = useState<AddProps<CellFamily>>()

    const cell_uuid = id_from_ref_props<string>(props)
    const api_handler = new CellsApi()
    const family_api_handler = new CellFamiliesApi()
    const cell_query = useQuery<AxiosResponse<AddProps<Cell>>, AxiosError>({
        queryKey: ['cell_retrieve', cell_uuid],
        queryFn: () => api_handler.cellsRetrieve(cell_uuid).then((r) => {
            console.log("Cell retrieve response", cell_uuid, r)
            if (r === undefined) return Promise.reject("No data in response")
            splitData(r.data)
            return r
        })
    })
    const family_query = useQuery<AxiosResponse<AddProps<CellFamily>>, AxiosError>({
        queryKey: ['cell_family_retrieve', family || "should_not_be_called"],
        queryFn: () => family_api_handler
            .cellFamiliesRetrieve(id_from_ref_props<string>(cell_query.data!.data.family))
            .then((r) => {
                if (r === undefined) return Promise.reject("No data in response")
                setFamilyData(r.data)
                return r
            }),
        enabled: !!family
    })

    // Mutations for saving edits
    const queryClient = useQueryClient()
    const cell_update_mutation = useMutation(
        (data: AddProps<PatchedCell>) => api_handler.cellsPartialUpdate(cell_uuid, data),
        {
            onSuccess: (data, variables, context) => {
                if (data === undefined) {
                    console.warn("No data in mutation response", {data, variables, context})
                    return
                }
                queryClient.setQueryData(['cell_retrieve', cell_uuid], data)
            },
            onError: (error, variables, context) => {
                console.error(error)
            },
        })

    const action = <CardActionBar
        type="cell"
        uuid={cell_uuid}
        path={PATHS.CELLS}
        family_uuid={cell_data?.family!}
        cycler_test_count={cell_data?.cycler_tests.length}
        editable={cell_data?.permissions.write!}
        editing={editing}
        setEditing={setEditing}
        onUndo={undoEditableData}
        onRedo={redoEditableData}
        undoable={editableDataHistoryIndex > 0}
        redoable={editableDataHistoryIndex < editableDataHistory.length - 1}
        onEditSave={() => {
            // _setCellData({...cell_data!, ...editableData})
            cell_update_mutation.mutate(editableData)
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
        expanded={expanded}
        setExpanded={setExpanded}
    />

    const loadingBody = <Card key={cell_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
        <CardHeader
            avatar={<CircularProgress sx={{color: (t) => t.palette.text.disabled}}/>}
            title={<A component={Link} to={`${PATHS.CELLS}/${cell_uuid}`}>{cell_uuid}</A>}
            subheader={<Stack direction="row" spacing={1}>
                <A component={Link} to={PATHS.CELLS}>Cell</A>
                <LoadingChip icon={<ICONS.TEAMS/>} />
            </Stack>}
            action={action}
        />
        {expanded? <CardContent>
            <Grid container>
                <LoadingChip icon={<ICONS.FAMILY/>}/>
            </Grid>
            <Grid container>
                <LoadingChip icon={<ICONS.CYCLER_TESTS/>}/>
            </Grid>
        </CardContent> : <CardContent />}
    </Card>

    const cardBody = <Card key={cell_uuid} className={clsx(classes.item_card)} {...props as CardProps}>
        <CardHeader
            avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
            title={<A component={Link} to={`${PATHS.CELLS}/${cell_uuid}`}>
                {`${family_data?.manufacturer} ${family_data?.model} ${cell_data?.identifier}`}
            </A>}
            subheader={<Stack direction="row" spacing={1} alignItems="center">
                <A component={Link} to={PATHS.CELLS}>Cell</A>
                <TeamChip url={cell_data?.team!} sx={{fontSize: "smaller"}}/>
            </Stack>}
            action={action}
        />
        {expanded? <CardContent sx={{maxHeight: editing? "80vh" : "unset", overflowY: "auto"}}>
            <Stack spacing={1}>
                <Divider key="read-props-header">Read-only properties</Divider>
                {cell_data && <PrettyObject
                    key="read-props"
                    target={readOnlyData}
                />}
                <Divider key="write-props-header">Editable properties</Divider>
                {cell_data && <PrettyObject
                    key="write-props"
                    target={editableData}
                    edit_mode={editing}
                    type_locked_keys={['identifier']}
                    onEdit={setEditableData}
                />}
                {family_data?.uuid && <Divider key="family-props-header">
                    Inherited from <CellFamilyChip uuid={family_data?.uuid}/>
                </Divider>}
                {family_data && <PrettyObject
                    target={family_data}
                    exclude_keys={[...Object.keys(cell_data!), 'cells']}
                />}
            </Stack>
        </CardContent> : <CardContent />}
    </Card>

    const getErrorBody: QueryDependentElement = (queries) => <ErrorCard
        status={queries.find(q => q.isError)?.error?.response?.status}
        header={
            <CardHeader
                avatar={<Avatar variant="square"><ICONS.CELLS/></Avatar>}
                title={cell_uuid}
                subheader={<Stack direction="row" spacing={1} alignItems="center">
                    <A component={Link} to={PATHS.CELLS}>Cell</A>
                </Stack>}
            />
        }
    />

    return <QueryWrapper
        queries={[cell_query, family_query]}
        loading={loadingBody}
        error={getErrorBody}
        success={cardBody}
    />
}