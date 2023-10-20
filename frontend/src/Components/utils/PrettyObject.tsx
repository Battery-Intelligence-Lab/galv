import TableContainer, {TableContainerProps} from "@mui/material/TableContainer";
import React, {forwardRef, ReactNode, useRef, useState} from "react";
import useStyles from "../../UseStyles";
import clsx from "clsx";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Prettify from "./Prettify";
import {SerializableObject, Serializable} from "./TypeChanger";

export type PrettyObjectProps = {
    target?: SerializableObject
    exclude_keys?: string[]
    type_locked_keys?: string[]
    nest_level?: number
    edit_mode?: boolean
    onEdit?: (value: SerializableObject) => void
    clearParentFocus?: () => void
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

export default function PrettyObject(
    {target, exclude_keys, type_locked_keys, nest_level, edit_mode, onEdit, clearParentFocus, ...table_props}:
        PrettyObjectProps & TableContainerProps) {

    const {classes} = useStyles()

    if (typeof target === 'undefined') {
        console.error("PrettyObject: target is undefined", {target, exclude_keys, type_locked_keys, nest_level, edit_mode, onEdit, clearParentFocus, ...table_props})
        return <></>
    }

    // Type coercion for optional props
    const _target = target || {}  // for tsLint
    const _edit_mode = edit_mode || false
    const _onEdit = onEdit || (() => {})
    const _nest_level = nest_level || 0
    const _exclude_keys = exclude_keys || ['url']
    const _type_locked_keys = type_locked_keys || []

    // Edit function factory produces a function that edits the object with a new value for key k
    const edit_fun_factory = (k: string) => (v: Serializable) => _onEdit({..._target, [k]: v})

    // Build a list of Prettify'd contents
    const keys = Object.keys(_target).filter(key => !_exclude_keys.includes(key))
    return <>
        <TableContainer
            className={clsx(
                classes.pretty_table,
                {[classes.pretty_nested]: _nest_level % 2}
            )}
            {...table_props as TableContainerProps}
        >
            <Table size="small">
                <TableBody>
                    {keys.map((key, i) => (
                        <TableRow key={i}>
                            <TableCell component="th" scope="row" key={`key_${i}`} align="right">
                                <Stack alignItems="stretch" justifyContent="flex-end">
                                    {_edit_mode && onEdit && !_type_locked_keys.includes(key) ?
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
                                        /> :
                                        <Typography variant="subtitle2" component="span" textAlign="right">
                                            {key}
                                        </Typography>
                                    }
                                </Stack>
                            </TableCell>
                            <TableCell width="90%" key={`value_${i}`} align="left">
                                <Stack alignItems="stretch" justifyContent="flex-start">
                                    <Prettify
                                        nest_level={_nest_level}
                                        edit_mode={_edit_mode}
                                        onEdit={edit_fun_factory(key)}
                                        target={_target[key]}
                                        allow_type_change={_edit_mode && !_type_locked_keys.includes(key)}
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
