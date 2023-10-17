import Card, {CardProps} from "@mui/material/Card";
import clsx from "clsx";
import CardContent from "@mui/material/CardContent";
import {Link} from "react-router-dom";
import React, {ReactElement} from "react";
import CardHeader, {CardHeaderProps} from "@mui/material/CardHeader";
import useStyles from "../../UseStyles";

export type ErrorProps = {
    status?: number | null | undefined
    message?: string
    detail?: string
    target?: string | number
}

export type ErrorPageProps = ErrorProps & {header?: ReactElement<CardHeaderProps>}

export default function ErrorPage(props: ErrorPageProps & CardProps) {
    const {classes} = useStyles();
    let content = <CardContent>
        {props.message}
    </CardContent>
    if (!props.message) {
        if (props.status === 401)
            content = <CardContent>You must <Link to={'/login'}>log in</Link> to see this item.</CardContent>
        else if (props.status === 403)
            content = <CardContent>You do not have permission to view this item.</CardContent>
        else if (props.status === 404)
            content = <CardContent>This item does not exist.</CardContent>
        else if (props.status && props.status >= 500)
            content = <CardContent>Something went wrong.</CardContent>
        else
            content = <CardContent>An unknown error occurred.</CardContent>
    }
    console.log("ErrorPage", props, content)
    return <Card className={clsx(classes.item_page, classes.error)} elevation={0} {...props as CardProps}>
        {props.header || <CardHeader avatar={"E"} title="Error"/>}
        {content}
    </Card>

}