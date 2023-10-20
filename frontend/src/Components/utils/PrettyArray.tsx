import React, {useEffect} from "react";
import {Container, Draggable, DropResult, OnDropCallback} from "react-smooth-dnd";
import {arrayMoveImmutable} from "array-move";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import DragHandleIcon from "@mui/icons-material/DragHandle";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {PrettyObjectProps} from "./PrettyObject";
import {ListProps} from "@mui/material";
import {useDebouncedCallback} from "use-debounce";
import Prettify from "./Prettify";
import useStyles from "../../UseStyles";
import clsx from "clsx";

type PrettyArrayProps = Pick<PrettyObjectProps, "nest_level" | "edit_mode" | "onEdit" | "clearParentFocus"> &
    {target: any[]}

export default function PrettyArray(
    {target, nest_level, edit_mode, onEdit, clearParentFocus, ...childProps}: PrettyArrayProps & ListProps
) {
    const _nest_level = nest_level || 0
    const _edit_mode = edit_mode || false
    const _onEdit = onEdit || (() => {})
    const _clearParentFocus = clearParentFocus || (() => {})

    const {classes} = useStyles()

    const [items, setItems] = React.useState([...target]);
    // const debounce = useDebouncedCallback((value: any[]) => _onEdit(value), 500)

    const onDrop: OnDropCallback = ({ removedIndex, addedIndex }: DropResult) => {
        if (removedIndex === null || addedIndex === null) return
        const newItems = arrayMoveImmutable(items, removedIndex, addedIndex)
        setItems(newItems);
        // debounce(newItems)
        _onEdit(newItems)
    };

    // Required to update the items in response to Undo/Redo
    useEffect(() => {setItems([...target])}, [target])

    return <List
        className={clsx(
            classes.pretty_array,
            {[classes.pretty_nested]: _nest_level % 2}
        )}
        dense={true}
        // onBlur={() => _onEdit(items)}
        {...childProps}
    >
        {
            _edit_mode?
                // @ts-ignore // types are not correctly exported by react-smooth-dnd
                <Container dragHandleSelector=".drag-handle" lockAxis="y" onDrop={onDrop}>
                    {items.map((item, i) => (
                        // @ts-ignore // types are not correctly exported by react-smooth-dnd
                        <Draggable key={i}>
                            <ListItem alignItems="flex-start">
                                <ListItemIcon key={`action_${i}`} className="drag-handle">
                                    <DragHandleIcon />
                                </ListItemIcon>
                                <Prettify
                                    key={`item_${i}`}
                                    target={item}
                                    nest_level={_nest_level}
                                    edit_mode={true}
                                    onEdit={(v) => {
                                        const newItems = [...items]
                                        newItems[i] = v
                                        setItems(newItems)
                                        // debounce(newItems)
                                        _onEdit(newItems)
                                    }}
                                    allow_type_change={true}
                                />
                            </ListItem>
                        </Draggable>
                    ))}
                    <ListItem key="new_item" alignItems="flex-start">
                        <Prettify
                            target=""
                            label="+ ITEM"
                            placeholder="enter new value"
                            nest_level={_nest_level}
                            edit_mode={true}
                            onEdit={(v) => {
                                const newItems = [...items]
                                newItems.push(v)
                                setItems(newItems)
                                // debounce(newItems)
                                _onEdit(newItems)
                                return ""
                            }}
                            allow_type_change={false}
                        />
                    </ListItem>
                </Container> :
                items.map((item, i) => <ListItem key={i} alignItems="flex-start">
                    <ListItemIcon key={`action_${i}`}>
                        <ArrowRightIcon />
                    </ListItemIcon>
                    <Prettify
                        key={i}
                        target={item}
                        nest_level={_nest_level}
                        edit_mode={false}
                    />
                </ListItem>)
        }
    </List>
}