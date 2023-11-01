import {CardProps} from "@mui/material";
import {ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {EquipmentFamily, Equipment} from "../../api_codegen";
import ChildCard, {AddProps} from "../utils/ChildCard";

export default function EquipmentCard(props: ObjectReferenceProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ChildCard<AddProps<Equipment>, AddProps<EquipmentFamily>>
        resource_id={uuid}
        lookup_key="EQUIPMENT"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}