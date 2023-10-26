import {CardProps} from "@mui/material";
import {ExpandableCardProps, usePropParamId} from "../utils/misc";
import {
    Cell,
    CellFamily,
} from "../../api_codegen";
import React from "react";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function CellCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Cell>, AddProps<CellFamily>>
        uuid={uuid}
        lookup_key="CELL"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}