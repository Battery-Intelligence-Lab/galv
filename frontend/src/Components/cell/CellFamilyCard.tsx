import {CardProps} from "@mui/material";
import { ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {
    CellFamiliesApi,
    CellFamily,
} from "../../api_codegen";
import React from "react";
import {AddProps} from "../utils/ResourceCard";
import ResourceFamilyCard from "../utils/ResourceFamilyCard";

export default function CellFamilyCard(props: Partial<ObjectReferenceProps> & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceFamilyCard<AddProps<CellFamily>>
        uuid={uuid}
        lookup_key="CELL_FAMILY"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "cells", "in_use", "team", "permissions"]}
        {...props}
    />
}