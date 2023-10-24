import {CardProps} from "@mui/material";
import { ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {
    EquipmentFamiliesApi,
    EquipmentFamily,
} from "../../api_codegen";
import React from "react";
import {AddProps} from "../utils/ResourceCard";
import ResourceFamilyCard from "../utils/ResourceFamilyCard";

export default function EquipmentFamilyCard(props: Partial<ObjectReferenceProps> & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceFamilyCard<AddProps<EquipmentFamily>>
        uuid={uuid}
        type="equipment_family"
        child_type="EQUIPMENT"
        api={EquipmentFamiliesApi}
        path_key="EQUIPMENT_FAMILIES"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "cells", "in_use", "team", "permissions"]}
        {...props}
    />
}