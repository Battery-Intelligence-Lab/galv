import {Link} from "react-router-dom";
import Badge, {BadgeProps} from "@mui/material/Badge";
import IconButton from "@mui/material/IconButton";
import clsx from "clsx";
import UseStyles from "../styles/UseStyles";
import Tooltip from "@mui/material/Tooltip";
import {ReactNode} from "react";

type CountBadgeProps = {
    icon: ReactNode
    url?: string
    tooltip?: ReactNode
}

export default function CountBadge(props: CountBadgeProps & BadgeProps) {
    const {classes} = UseStyles();
    let content =
        <Badge overlap="circular" className={clsx(classes.countBadge)} {...props as BadgeProps}>
        <IconButton disabled={!props.url || props.badgeContent === 0}>
            {props.icon}
        </IconButton>
    </Badge>
    if (props.tooltip) {content = <Tooltip title={props.tooltip} describeChild={true}>{content}</Tooltip>}
    return props.url && props.badgeContent !== 0? <Link to={props.url}>{content}</Link> : content
}