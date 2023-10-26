import {CardProps} from "@mui/material";
import {ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {EquipmentFamily, Equipment} from "../../api_codegen";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function EquipmentCard(props: ObjectReferenceProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Equipment>, AddProps<EquipmentFamily>>
        uuid={uuid}
        lookup_key="EQUIPMENT"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}