import {CardProps} from "@mui/material";
import {ObjectReferenceProps, usePropParamId} from "../utils/misc";
import {EquipmentFamily, Equipment} from "../../api_codegen";
import ResourceCard, {AddProps} from "../utils/ResourceCard";

export default function EquipmentCard(props: ObjectReferenceProps & CardProps) {
    const uuid = usePropParamId<string>(props)

    return <ResourceCard<AddProps<Equipment>>
        resource_id={uuid}
        lookup_key="EQUIPMENT"
        editing={false}
        expanded={false}
        {...props}
    />
}