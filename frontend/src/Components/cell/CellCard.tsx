import {CardProps} from "@mui/material";
import {ExpandableCardProps, usePropParamId} from "../utils/misc";
import {Cell} from "../../api_codegen";
import React from "react";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function CellCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Cell>>
        resource_id={uuid}
        lookup_key="CELL"
        editing={false}
        expanded={false}
        {...props}
    />
}