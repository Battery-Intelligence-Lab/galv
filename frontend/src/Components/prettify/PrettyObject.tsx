import TableContainer, {TableContainerProps} from "@mui/material/TableContainer";
import React from "react";
import useStyles from "../../styles/UseStyles";
import clsx from "clsx";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Prettify from "./Prettify";
import {SerializableObject, Serializable} from "../TypeChanger";
import {API_HANDLERS, API_SLUGS, Field, FIELDS, LookupKey, PRIORITY_LEVELS} from "../../constants";
import {AxiosError, AxiosResponse} from "axios";
import {useQuery} from "@tanstack/react-query";
import {BaseResource} from "../ResourceCard";

export type PrettyObjectProps = {
    target?: SerializableObject
    lookup_key?: LookupKey
    nest_level?: number
    edit_mode?: boolean
    creating?: boolean
    onEdit?: (value: SerializableObject) => void
}

function rename_key_in_place(
    obj: SerializableObject,
    old_key: string,
    new_key: string
): SerializableObject {
    const new_obj: PrettyObjectProps["target"] = {}
    Object.entries(obj).forEach(([k, v]) => {
        if (k === old_key) {
            if (new_key !== "")
                new_obj[new_key] = v
        } else new_obj[k] = v
    })
    return new_obj
}

export function PrettyObjectFromQuery<T extends BaseResource>(
    { resource_id, lookup_key, filter, ...prettyObjectProps}:
        {
            resource_id: string|number,
            lookup_key: LookupKey,
            filter?: (d: any, lookup_key: LookupKey) => any
        } & Omit<PrettyObjectProps, "target">
) {
    const target_api_handler = new API_HANDLERS[lookup_key]()
    const target_get = target_api_handler[
        `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof target_api_handler
        ] as (uuid: string) => Promise<AxiosResponse<T>>

    const target_query = useQuery<AxiosResponse<T>, AxiosError>({
        queryKey: [lookup_key, resource_id],
        queryFn: () => target_get.bind(target_api_handler)(String(resource_id))
    })

    return <PrettyObject
        {...prettyObjectProps}
        target={filter? filter(target_query.data?.data, lookup_key) : target_query.data?.data}
    />
}

export default function PrettyObject(
    {target, lookup_key, nest_level, edit_mode, creating, onEdit, ...table_props}:
        PrettyObjectProps & TableContainerProps) {

    const {classes} = useStyles()

    if (typeof target === 'undefined') {
        console.error("PrettyObject: target is undefined", {target, lookup_key, nest_level, edit_mode, creating, onEdit, ...table_props})
        return <></>
    }

    // Type coercion for optional props
    const _target = target || {}  // for tsLint
    const _edit_mode = edit_mode || false
    const _onEdit = onEdit || (() => {})
    const _nest_level = nest_level || 0

    const get_metadata = (key: string) => {
        if (lookup_key !== undefined) {
            const fields = FIELDS[lookup_key]
            if (Object.keys(fields).includes(key))
                return FIELDS[lookup_key][key as keyof typeof fields] as Field
        }
        return undefined
    }
    const is_readonly = (key: string) => get_metadata(key)?.readonly && (!creating || !get_metadata(key)?.createonly)

    // Edit function factory produces a function that edits the object with a new value for key k
    const edit_fun_factory = (k: string) => (v: Serializable) => _onEdit({..._target, [k]: v})

    // Build a list of Prettify'd contents
    const keys = Object.keys(_target).filter(key => get_metadata(key)?.priority !== PRIORITY_LEVELS.HIDDEN)
    return <>
        <TableContainer
            className={clsx(
                classes.prettyTable,
                {[classes.prettyNested]: _nest_level % 2, edit_mode: _edit_mode},
            )}
            {...table_props as TableContainerProps}
        >
            <Table size="small">
                <TableBody>
                    {keys.map((key, i) => (
                        <TableRow key={i}>
                            <TableCell component="th" scope="row" key={`key_${i}`} align="right">
                                <Stack alignItems="stretch" justifyContent="flex-end">
                                    {_edit_mode && onEdit && !is_readonly(key) ?
                                        <Prettify
                                            nest_level={_nest_level}
                                            edit_mode={true}
                                            hide_type_changer={true}
                                            onEdit={(new_key) => {
                                                // Rename key (or delete if new_key is empty)
                                                try {new_key = String(new_key)} catch (e) {new_key = ""}
                                                _onEdit(rename_key_in_place(_target, key, new_key))
                                            }}
                                            target={key}
                                            label="key"
                                            fullWidth={true}
                                        /> :
                                        <Typography variant="subtitle2" component="span" textAlign="right">
                                            {key}
                                        </Typography>
                                    }
                                </Stack>
                            </TableCell>
                            <TableCell key={`value_${i}`} align="left">
                                <Stack alignItems="stretch" justifyContent="flex-start">
                                    <Prettify
                                        nest_level={_nest_level}
                                        edit_mode={_edit_mode}
                                        onEdit={edit_fun_factory(key)}
                                        target={_target[key]}
                                        lock_type_to={get_metadata(key)?.many? "array" : get_metadata(key)?.type}
                                        lock_child_type_to={get_metadata(key)?.many? get_metadata(key)?.type : undefined}
                                    />
                                </Stack>
                            </TableCell>
                        </TableRow>))}
                    {_edit_mode && <TableRow key="add_new">
                        <TableCell component="th" scope="row" key="add_key" align="right">
                            <Prettify
                                nest_level={_nest_level}
                                edit_mode={_edit_mode}
                                hide_type_changer={true}
                                target=""
                                placeholder="new_object_key"
                                label="+ KEY"
                                multiline={false}
                                onEdit={(new_key: Serializable) => {
                                    // Add new key
                                    try {new_key = String(new_key)} catch (e) {return ""}
                                    const new_obj = {..._target}
                                    if (new_key !== "")
                                        new_obj[new_key] = ""
                                    _onEdit!(new_obj)
                                    return ""
                                }}
                            />
                        </TableCell>
                        <TableCell key="add_value">
                            <em>Enter a new key then click here to create a new entry</em>
                        </TableCell>
                    </TableRow>}
                </TableBody>
            </Table>
        </TableContainer>
    </>
}
