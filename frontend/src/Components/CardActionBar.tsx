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
import {Link} from "react-router-dom";
import RemoveIcon from "@mui/icons-material/Remove";
import AddIcon from "@mui/icons-material/Add";
import {
    DISPLAY_NAMES,
    DISPLAY_NAMES_PLURAL,
    FIELDS,
    is_lookup_key,
    LookupKey,
    PATHS,
} from "../constants";
import {useApiResource} from "./ApiResourceContext";
import LookupKeyIcon from "./LookupKeyIcon";
import {BaseResource} from "./ResourceCard";
import {SvgIconProps} from "@mui/material/SvgIcon";
import {id_from_ref_props} from "./misc";
import clsx from "clsx";
import UseStyles from "../styles/UseStyles";

type CardActionBarProps = {
    lookup_key: LookupKey
    resource_id?: string|number
    excludeContext?: boolean
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
    iconProps?: Partial<SvgIconProps>
}

/**
 *
 * @param props.onEditSave function that returns true if the save was successful. If false, the editing state will not change.
 * @param props.onEditDiscard function that returns true if the discard was successful. If false, the editing state will not change.
 *
 * @constructor
 */
export default function CardActionBar(props: CardActionBarProps) {

    const {classes} = UseStyles()
    const {apiResource} = useApiResource()
    const iconProps: Partial<SvgIconProps> = {
        fontSize: "large",
        ...props.iconProps
    }

    const context_section = <>{
        Object.entries(FIELDS[props.lookup_key])
            .filter(([k, v]) => is_lookup_key(v.type))
            .map(([k, v]) => {
                const relative_lookup_key = v.type as LookupKey
                let content: ReactNode
                if (v.many) {
                    const relative_value = apiResource?.[k] as BaseResource[]|undefined
                    content = <CountBadge
                        key={`highlight`}
                        icon={<LookupKeyIcon lookupKey={relative_lookup_key} tooltip={false} {...iconProps}/>}
                        badgeContent={relative_value?.length}
                        url={PATHS[relative_lookup_key]}
                    />
                } else {
                    const relative_value = apiResource?.[k] as BaseResource|undefined
                    const relative_id = relative_value? id_from_ref_props(relative_value) : undefined
                    content = <IconButton
                        component={Link}
                        to={`${PATHS[relative_lookup_key]}/${relative_id}`
                        }>
                        <LookupKeyIcon lookupKey={relative_lookup_key} tooltip={false} {...iconProps}/>
                    </IconButton>
                }
                return <Tooltip
                    title={`View ${(v.many? DISPLAY_NAMES_PLURAL: DISPLAY_NAMES)[relative_lookup_key]}`}
                    arrow
                    describeChild
                    key={k}
                >
                    <div>{content}</div>
                </Tooltip>
            })
    }</>

    let edit_section: ReactNode
    if (props.editable) {
        if (typeof props.setEditing !== 'function')
            throw new Error(`setEditing must be a function if editable=true`)
        if (typeof props.onEditSave !== 'function')
            throw new Error(`onEditSave must be a function if editable=true`)
        if (typeof props.onEditDiscard !== 'function')
            throw new Error(`onEditDiscard must be a function if editable=true`)
        if (!props.editing) {
            edit_section = <Tooltip
                title={`Edit this ${DISPLAY_NAMES[props.lookup_key]}`}
                arrow
                describeChild
                key="edit"
            >
                <IconButton onClick={() => props.setEditing!(true)}>
                    <EditIcon {...iconProps}/>
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
                    <UndoIcon {...iconProps}/>
                </IconButton>
                </span>
                </Tooltip>}
                {props.onRedo && <Tooltip title={`Redo`} arrow describeChild key="redo">
                    <span>
                    <IconButton onClick={props.onRedo!} disabled={!props.redoable}>
                        <RedoIcon {...iconProps}/>
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
                        <SaveIcon {...iconProps} color="success"/>
                    </IconButton>
                </Tooltip>
                {undo_buttons}
                <Tooltip title={`Discard changes`} arrow describeChild key="discard">
                    <IconButton onClick={() => {
                        if (props.onEditDiscard!())
                            props.setEditing!(false)
                    }}>
                        <CloseIcon {...iconProps} color="error"/>
                    </IconButton>
                </Tooltip>
            </>
        }
    }

    return <Stack direction="row" spacing={1} alignItems="center">
        {!props.excludeContext && context_section}
        {props.editable && edit_section}
        {props.destroyable && <Tooltip
            title={`Delete this ${DISPLAY_NAMES[props.lookup_key]}`}
            arrow
            describeChild
            key="delete"
        >
            <IconButton component={Link} to={`${PATHS[props.lookup_key]}/${props.resource_id}/delete`}>
                <EditIcon className={clsx(classes.deleteIcon)} {...iconProps}/>
            </IconButton>
        </Tooltip>}
        {props.expanded !== undefined &&
            props.setExpanded !== undefined &&
            <Tooltip title={props.expanded ? "Hide Details" : "Show Details"} arrow describeChild key="expand">
                <IconButton onClick={() => props.setExpanded!(!props.expanded)}>
                    {props.expanded ? <RemoveIcon {...iconProps}/> : <AddIcon {...iconProps}/>}
                </IconButton>
            </Tooltip>}
    </Stack>
}