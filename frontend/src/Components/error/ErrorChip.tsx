import Chip, {ChipProps} from "@mui/material/Chip";
import clsx from "clsx";
import React, {ReactNode} from "react";
import useStyles from "../../styles/UseStyles";
import {ErrorProps} from "./ErrorPage";
import Tooltip from "@mui/material/Tooltip";
import {useCurrentUser} from "../CurrentUserContext";
import Button from "@mui/material/Button";

export default function ErrorChip(props: ErrorProps & ChipProps) {
    const {classes} = useStyles();
    const {setLoginFormOpen} = useCurrentUser()
    let content: ReactNode = props.message || ""
    if (!props.message) {
        if (props.status === 401)
            content = <Button onClick={() => setLoginFormOpen(true)}>Log in required</Button>
        else if (props.status === 403)
            content = `Permission denied.`
        else if (props.status === 404)
            content = `Not found.`
        else if (props.status && props.status >= 500)
            content = `Server error.`
        else
            content = `Unknown error.`
    }
    return <Tooltip
        title={<>{props.status} Error: {props.detail || 'No more information is available'}</>}
        arrow
        describeChild
    >
        <Chip
            className={clsx(classes.itemChip, classes.error)}
            label={content as ReactNode}
            {...props as ChipProps}
        />
    </Tooltip>

}