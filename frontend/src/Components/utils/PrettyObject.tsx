import TableContainer, {TableContainerProps} from "@mui/material/TableContainer";
import React, {ReactNode, useRef, useState} from "react";
import useStyles from "../../UseStyles";
import clsx from "clsx";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import Popper from "@mui/material/Popper";
import Tooltip from "@mui/material/Tooltip";
import IconButton from "@mui/material/IconButton";
import ClearIcon from "@mui/icons-material/Clear";
import Prettify from "./Prettify";
import TypeChanger from "./TypeChanger";

export type PrettyObjectProps = {
    target: { [key: string]: any }
    exclude_keys?: string[]
    type_locked_keys?: string[]
    nest_level?: number
    edit_mode?: boolean
    onEdit?: (value: { [key: string]: any }) => void
    clearParentFocus?: () => void
}

export default function PrettyObject(
    {target, exclude_keys, type_locked_keys, nest_level, edit_mode, onEdit, clearParentFocus, ...table_props}:
        PrettyObjectProps & TableContainerProps) {
    const [focusKey, setFocusKey] = useState<string | null>(null)
    const [focusElement, setFocusElement] = useState<HTMLElement | null>(null)

    const popperElements = useRef<(HTMLDivElement|null)[]>([]);

    const {classes} = useStyles()

    // Type coercion for optional props
    const _edit_mode = edit_mode || false
    const _onEdit = onEdit || (() => {})
    const _nest_level = nest_level || 0
    const _clearParentFocus = clearParentFocus || (() => {})
    const _exclude_keys = exclude_keys || ['url']
    const _type_locked_keys = type_locked_keys || []
    
    // Edit function factory produces a function that edits the object with a new value for key k
    const edit_fun_factory = (k: string) =>
        (v: Partial<PrettyObjectProps["target"]>) => _onEdit({...target, [k]: v})
    const clearFocus = () => {setFocusKey(null); setFocusElement(null)}

    // Build a list of Prettify'd contents
    const keys = Object.keys(target).filter(key => !_exclude_keys.includes(key))
    const prettified_target: { [key: string]: ReactNode } = {}
    keys.forEach(key => {
        const v: any = target[key]
        if (v === null || v === undefined) return
        prettified_target[key] = <Prettify
            nest_level={_nest_level}
            edit_mode={_edit_mode}
            onEdit={edit_fun_factory(key)}
            target={v}
            clearParentFocus={clearFocus}
        />
    })
    return <TableContainer
        className={clsx(
            "PrettyObjectTableContainer",
            classes.pretty_table,
            {[classes.pretty_nested]: _nest_level % 2}
        )}
        onBlur={(e) => {
            console.log(e)
            e.stopPropagation()
            if (e.relatedTarget instanceof HTMLElement) {
                // If element is a part of a popover for this Table's immediate rows, do not clear focus
                const popper = e.relatedTarget.classList.contains('PrettyObjectTypeChangePopper')?
                    e.relatedTarget : e.relatedTarget.closest('.PrettyObjectTypeChangePopper')
                if (popper && popperElements.current.find((el) => popper.isSameNode(el))) return
            }
            clearFocus()
        }}
        {...table_props as TableContainerProps}
    >
        <Table size="small">
            <TableBody>
                {Object.entries(prettified_target).map(([key, value], i) => (
                    <TableRow
                        onFocus={(e) => {
                            // Only the nearest PrettyObjectTableContainer should have focus
                            const target_container = e.target.closest('.PrettyObjectTableContainer')
                            const own_container = e.currentTarget.closest('.PrettyObjectTableContainer')
                            if (!target_container || !target_container.isSameNode(own_container)) return
                            _clearParentFocus()
                            setFocusElement(e.currentTarget)
                            setFocusKey(key)
                        }}
                        key={i}
                    >
                        <TableCell component="th" scope="row" key={`key_${i}`} align="right">
                            <Stack>
                                {_edit_mode && !_type_locked_keys.includes(key) ?
                                    <Prettify
                                        nest_level={_nest_level}
                                        edit_mode={_edit_mode}
                                        onEdit={(new_key: string) => {
                                            // Rename key (or delete if new_key is empty)
                                            const new_obj = {...target}
                                            if (new_key !== "")
                                                new_obj[new_key] = target[key]
                                            delete new_obj[key]
                                            _onEdit!(new_obj)
                                        }}
                                        target={key}
                                    /> :
                                    <Typography key={`name_${i}`} variant="subtitle2" component="span"
                                                textAlign="right">
                                        {key}
                                    </Typography>
                                }
                                {_edit_mode &&
                                    <Popper
                                        className={clsx("PrettyObjectTypeChangePopper")}
                                        ref={el => popperElements.current[i] = el}
                                        open={key === focusKey}
                                        anchorEl={focusElement}
                                        placement="top"
                                        sx={{backgroundColor: (t) => t.palette.background.paper}}
                                    >
                                        <Stack direction="row" spacing={0.5} key={`typechanger_${i}`}>
                                            <TypeChanger
                                                key={`typechanger_${i}`}
                                                currentValue={target[key]}
                                                onTypeChange={edit_fun_factory(key)}
                                                disabled={_type_locked_keys.includes(key) || false}
                                            />
                                            <Tooltip
                                                title={_type_locked_keys.includes(key) ?
                                                    "This value cannot be removed" : `Remove ${key}`}
                                                arrow
                                                describeChild
                                                key={`remove_${i}`}
                                            >
                                <span>
                                    <IconButton
                                        onClick={() => {
                                            // Remove key
                                            clearFocus()
                                            const new_obj = {...target}
                                            delete new_obj[key]
                                            _onEdit!(new_obj)
                                        }}
                                        disabled={_type_locked_keys.includes(key) || false}
                                    >
                                        <ClearIcon color="error"/>
                                    </IconButton>
                                </span>
                                            </Tooltip>
                                        </Stack>
                                    </Popper>
                                }
                            </Stack>
                        </TableCell>
                        <TableCell width="90%" key={`value_${i}`} align="left">{value}</TableCell>
                    </TableRow>))}
            </TableBody>
        </Table>
    </TableContainer>
}
