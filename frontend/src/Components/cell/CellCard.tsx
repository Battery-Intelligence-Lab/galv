import {CardProps} from "@mui/material";
import {ExpandableCardProps, usePropParamId} from "../utils/misc";
import {
    Cell,
    CellFamily,
} from "../../api_codegen";
import React from "react";
import MetadataCard, {AddProps} from "../utils/MetadataCard";

export default function CellCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <MetadataCard<AddProps<Cell>, AddProps<CellFamily>>
        resource_id={uuid}
        lookup_key="CELL"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}