import {CardProps} from "@mui/material";
import { ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {
    CellFamiliesApi,
    CellFamily,
} from "../../api_codegen";
import React from "react";
import {AddProps} from "../utils/MetadataCard";
import MetadataFamilyCard from "../utils/MetadataFamilyCard";

export default function CellFamilyCard(props: Partial<ObjectReferenceProps> & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <MetadataFamilyCard<AddProps<CellFamily>>
        family_id={uuid}
        lookup_key="CELL_FAMILY"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "cells", "in_use", "team", "permissions"]}
        {...props}
    />
}