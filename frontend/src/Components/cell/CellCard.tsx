import {CardProps} from "@mui/material";
import {ExpandableCardProps, usePropParamId} from "../utils/misc";
import {
    Cell,
    CellFamiliesApi,
    CellFamily,
    CellsApi
} from "../../api_codegen";
import React from "react";
import CellFamilyChip from "./CellFamilyChip";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function CellCard(props: ExpandableCardProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Cell>, AddProps<CellFamily>>
        target_uuid={uuid}
        target_type="cells"
        target_api={CellsApi}
        family_api={CellFamiliesApi}
        FamilyChip={CellFamilyChip}
        path_key="CELLS"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}