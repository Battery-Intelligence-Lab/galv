import React, {ReactNode} from "react";
import Tooltip from "@mui/material/Tooltip";
import IconButton from "@mui/material/IconButton";
import EditIcon from "@mui/icons-material/Edit";
import UndoIcon from "@mui/icons-material/Undo";
import RedoIcon from "@mui/icons-material/Redo";
import SaveIcon from "@mui/icons-material/Save";
import CloseIcon from "@mui/icons-material/Close";
import Stack from "@mui/material/Stack";
import CountBadge from "./CountBadge";
import {ICONS} from "../../icons";
import {PATHS} from "../../App";
import {Link} from "react-router-dom";
import ManageSearchIcon from "@mui/icons-material/ManageSearch";
import RemoveIcon from "@mui/icons-material/Remove";
import AddIcon from "@mui/icons-material/Add";
import {type_to_family_type} from "./ResourceCard";

type CardActionBarProps = {
    type: string
    uuid?: string
    path?: string
    family_uuid?: string
    highlight_count?: number
    highlight_icon_key?: keyof typeof ICONS
    highlight_path?: string
    highlight_tooltip?: ReactNode
    editable?: boolean
    editing?: boolean
    setEditing?: (editing: boolean) => void
    onEditSave?: () => boolean
    onEditDiscard?: () => boolean
    undoable?: boolean
    redoable?: boolean
    onUndo?: () => void
    onRedo?: () => void
    destroyable?: boolean
    expanded?: boolean
    setExpanded?: (expanded: boolean) => void
}

/**
 *
 * @param props.onEditSave function that returns true if the save was successful. If false, the editing state will not change.
 * @param props.onEditDiscard function that returns true if the discard was successful. If false, the editing state will not change.
 *
 * @constructor
 */
export default function CardActionBar(props: CardActionBarProps) {
    const typeName = (props.type.charAt(0).toUpperCase() + props.type.slice(1)).replace(/_/g, ' ')

    let edit_section: ReactNode
    if (props.editable) {
        if (typeof props.setEditing !== 'function')
            throw new Error(`setEditing must be a function if editable=true`)
        if (typeof props.onEditSave !== 'function')
            throw new Error(`onEditSave must be a function if editable=true`)
        if (typeof props.onEditDiscard !== 'function')
            throw new Error(`onEditDiscard must be a function if editable=true`)
        if (!props.editing) {
            edit_section = <Tooltip title={`Edit this ${typeName}`} arrow describeChild key="edit">
                <IconButton onClick={() => props.setEditing!(true)}>
                    <EditIcon fontSize="large"/>
                </IconButton>
            </Tooltip>
        } else {
            if (props.undoable && typeof props.onUndo !== 'function')
                throw new Error(`onUndo must be a function if undoable=true`)
            if (props.redoable && typeof props.onRedo !== 'function')
                throw new Error(`onRedo must be a function if redoable=true`)
            const undo_buttons = <>
                {props.onUndo && <Tooltip title={`Undo`} arrow describeChild key="undo">
                <span>
                <IconButton onClick={props.onUndo!} disabled={!props.undoable}>
                    <UndoIcon fontSize="large"/>
                </IconButton>
                </span>
                </Tooltip>}
                {props.onRedo && <Tooltip title={`Redo`} arrow describeChild key="redo">
                    <span>
                    <IconButton onClick={props.onRedo!} disabled={!props.redoable}>
                        <RedoIcon fontSize="large"/>
                    </IconButton>
                    </span>
                </Tooltip>}
            </>

            edit_section = <>
                <Tooltip title={`Save changes`} arrow describeChild key="save">
                    <IconButton onClick={() => {
                        if (props.onEditSave!())
                            props.setEditing!(false)
                    }}>
                        <SaveIcon fontSize="large" color="success"/>
                    </IconButton>
                </Tooltip>
                {undo_buttons}
                <Tooltip title={`Discard changes`} arrow describeChild key="discard">
                    <IconButton onClick={() => {
                        if (props.onEditDiscard!())
                            props.setEditing!(false)
                    }}>
                        <CloseIcon fontSize="large" color="error"/>
                    </IconButton>
                </Tooltip>
            </>
        }
    }

    const ICON = props.highlight_icon_key? ICONS[props.highlight_icon_key] : ICONS.DASHBOARD

    return <Stack direction="row" spacing={1} alignItems="center">
        {props.highlight_count && <CountBadge
            key={`highlight`}
            icon={<ICON fontSize="large"/>}
            badgeContent={props.highlight_count}
            url={props.highlight_path}
            tooltip={props.highlight_tooltip}
        />}
        {props.editable && edit_section}
        {props.destroyable && <Tooltip title={`Delete this ${typeName}`} arrow describeChild key="delete">
            <IconButton component={Link} to={`${props.path}/${props.uuid}/delete`}>
                <EditIcon fontSize="large"/>
            </IconButton>
        </Tooltip>}
        <Tooltip title={`Go to ${typeName} Page`} arrow describeChild key="goto">
            <IconButton component={Link} to={`${props.path}/${props.uuid}`}>
                <ManageSearchIcon fontSize="large"/>
            </IconButton>
        </Tooltip>
        {props.family_uuid && props.path ? <Tooltip title={`Go to ${typeName} Family Page`} arrow describeChild key="family">
                <IconButton component={Link} to={`${type_to_family_type(props.path)}_families/${props.family_uuid}`}>
                    <ICONS.FAMILY fontSize="large"/>
                </IconButton>
            </Tooltip> :
            <IconButton disabled={true}>
                <ICONS.FAMILY fontSize="large"/>
            </IconButton>}
        {props.expanded !== undefined &&
            props.setExpanded !== undefined &&
            <Tooltip title={props.expanded ? "Hide Details" : "Show Details"} arrow describeChild key="expand">
                <IconButton onClick={() => props.setExpanded!(!props.expanded)}>
                    {props.expanded ? <RemoveIcon fontSize="large"/> : <AddIcon fontSize="large"/>}
                </IconButton>
            </Tooltip>}
    </Stack>
}