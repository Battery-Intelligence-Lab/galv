import {CardProps} from "@mui/material";
import { ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {
    EquipmentFamiliesApi,
    EquipmentFamily,
} from "../../api_codegen";
import React from "react";
import {AddProps} from "../utils/MetadataCard";
import MetadataFamilyCard from "../utils/MetadataFamilyCard";

export default function EquipmentFamilyCard(props: Partial<ObjectReferenceProps> & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <MetadataFamilyCard<AddProps<EquipmentFamily>>
        family_id={uuid}
        lookup_key="EQUIPMENT_FAMILY"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "cells", "in_use", "team", "permissions"]}
        {...props}
    />
}