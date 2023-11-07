import Chip, {ChipProps} from "@mui/material/Chip";
import useStyles from "../UseStyles";
import clsx from "clsx";
import CircularProgress from "@mui/material/CircularProgress";
import {Link} from "react-router-dom";
import React from "react";


export default function LoadingChip(props: {url?: string, icon: JSX.Element} & ChipProps) {
    const { classes } = useStyles();
    return props.url? <Chip
        key={props.url}
        className={clsx(classes.item_chip)}
        variant="outlined"
        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
        component={Link}
        icon={props.icon}
        to={props.url}
        clickable={true}
        {...props as ChipProps as any}
    /> : <Chip
        className={clsx(classes.item_chip)}
        disabled={true}
        variant="outlined"
        label={<CircularProgress size="1.5em" sx={{color: (t) => t.palette.text.disabled}}/>}
        icon={props.icon}
        {...props as ChipProps as any}
    />
}
