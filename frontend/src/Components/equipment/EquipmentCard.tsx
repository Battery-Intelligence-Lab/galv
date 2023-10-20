import {CardProps} from "@mui/material";
import {id_from_ref_props, ObjectReferenceProps} from "../utils/misc";
import {EquipmentFamiliesApi, EquipmentApi, EquipmentFamily, Equipment} from "../../api_codegen";
import ResourceCard, {AddProps} from "../utils/ResourceCard";
import EquipmentFamilyChip from "./EquipmentFamilyChip";

export default function EquipmentCard(props: ObjectReferenceProps & CardProps) {
    const equipment_uuid = id_from_ref_props<string>(props)

    return <ResourceCard<AddProps<Equipment>, AddProps<EquipmentFamily>>
        target_uuid={equipment_uuid}
        target_type="equipment"
        target_api={EquipmentApi}
        family_api={EquipmentFamiliesApi}
        FamilyChip={EquipmentFamilyChip}
        path_key="EQUIPMENT"
        editing={false}
        expanded={false}
        read_only_fields={["uuid", "url", "family", "in_use", "team", "cycler_tests", "permissions"]}
        {...props}
    />
}