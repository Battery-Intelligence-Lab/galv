import PollIcon from "@mui/icons-material/Poll";
import MultilineChartIcon from "@mui/icons-material/MultilineChart";
import DatasetLinkedIcon from "@mui/icons-material/DatasetLinked";
import BatteryFullIcon from "@mui/icons-material/BatteryFull";
import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
import HomeIcon from "@mui/icons-material/Home";
import AssignmentIcon from "@mui/icons-material/Assignment";
import HolidayVillageIcon from "@mui/icons-material/HolidayVillage";
import PeopleAltIcon from "@mui/icons-material/PeopleAlt";
import BatchPredictionIcon from '@mui/icons-material/BatchPrediction';

import {
    CellFamiliesApi, CellsApi, CyclerTestsApi, EquipmentApi,
    EquipmentFamiliesApi, ExperimentsApi,
    FilesApi, LabsApi,
    ScheduleFamiliesApi, SchedulesApi,
    TeamsApi
} from "./api_codegen";
import {TypeChangerSupportedTypeName} from "./Components/utils/TypeChanger";

/**
 * This is a list of various resources grouped under a common name for each
 * resource type.
 * This allows us to pass a single identifier for the resource type to
 * various components, which can then use this identifier to determine
 * which API to use, which icon to display, etc.
 */

/**
 * Icons for each resource type.
 * Currently all families share the same icon.
 */
export const ICONS = {
    FILE: PollIcon,
    CELL_FAMILY: BatchPredictionIcon,
    EQUIPMENT_FAMILY: BatchPredictionIcon,
    SCHEDULE_FAMILY: BatchPredictionIcon,
    DASHBOARD: HomeIcon,
    EXPERIMENT: DatasetLinkedIcon,
    CYCLER_TEST: MultilineChartIcon,
    CELL: BatteryFullIcon,
    EQUIPMENT: PrecisionManufacturingIcon,
    SCHEDULE: AssignmentIcon,
    LAB: HolidayVillageIcon,
    TEAM: PeopleAltIcon
} as const

/**
 * Paths used by React Router to route to each resource type.
 * This deliberately mimics paths on the API because they are
 * used to determine resource types when parsing URLs that look
 * like they might be resource URLs.
 */
export const PATHS = {
    FILE: "/files",
    DASHBOARD: "/",
    EXPERIMENT: "/experiments",
    CYCLER_TEST: "/cycler_tests",
    DATASET: "/datasets",
    CELL: "/cells",
    CELL_FAMILY: "/cell_families",
    EQUIPMENT: "/equipment",
    EQUIPMENT_FAMILY: "/equipment_families",
    SCHEDULE: "/schedules",
    SCHEDULE_FAMILY: "/schedule_families",
    LAB: "/labs",
    TEAM: "/teams",
    USER: "/users",
    PROFILE: "/profile",
    TOKEN: "/tokens",
} as const

/**
 * Display names are in Title Case.
 */
export const DISPLAY_NAMES = {
    FILE: "File",
    DASHBOARD: "Dashboard",
    EXPERIMENT: "Experiment",
    CYCLER_TEST: "Cycler Test",
    DATASET: "Dataset",
    CELL: "Cell",
    CELL_FAMILY: "Cell Family",
    EQUIPMENT: "Equipment",
    EQUIPMENT_FAMILY: "Equipment Family",
    SCHEDULE: "Schedule",
    SCHEDULE_FAMILY: "Schedule Family",
    LAB: "Lab",
    TEAM: "Team",
    USER: "User",
    PROFILE: "Profile",
    TOKEN: "Token",
} as const

/**
 * Title Case, as with DISPLAY_NAMES. Plural.
 */
export const DISPLAY_NAMES_PLURAL = {
    FILE: "Files",
    DASHBOARD: "Dashboard",
    EXPERIMENT: "Experiments",
    CYCLER_TEST: "Cycler Tests",
    DATASET: "Datasets",
    CELL: "Cells",
    CELL_FAMILY: "Cell Families",
    EQUIPMENT: "Equipment",
    EQUIPMENT_FAMILY: "Equipment Families",
    SCHEDULE: "Schedules",
    SCHEDULE_FAMILY: "Schedule Families",
    LAB: "Labs",
    TEAM: "Teams",
    USER: "Users",
    PROFILE: "Profile",
    TOKEN: "Tokens",
} as const

/**
 * API handlers for each resource type.
 * Instantiated with new API_HANDLERS[lookup_key]().
 */
export const API_HANDLERS = {
    FILE: FilesApi,
    CELL_FAMILY: CellFamiliesApi,
    EQUIPMENT_FAMILY: EquipmentFamiliesApi,
    SCHEDULE_FAMILY: ScheduleFamiliesApi,
    EXPERIMENT: ExperimentsApi,
    CYCLER_TEST: CyclerTestsApi,
    CELL: CellsApi,
    EQUIPMENT: EquipmentApi,
    SCHEDULE: SchedulesApi,
    LAB: LabsApi,
    TEAM: TeamsApi,
} as const

/**
 * API slugs for each resource type.
 * Used to access the inner API functions.
 *
 * Casting is likely to be necessary when using this, e.g.:
 * ```
 * const target_get = target_api_handler[
 *         `${API_SLUGS[lookup_key]}Retrieve` as keyof typeof target_api_handler
 *         ] as (uuid: string) => Promise<AxiosResponse<T>>
 * ```
 */
export const API_SLUGS = {
    CELL: "cells",
    EQUIPMENT: "equipment",
    SCHEDULE: "schedules",
    CELL_FAMILY: "cellFamilies",
    EQUIPMENT_FAMILY: "equipmentFamilies",
    SCHEDULE_FAMILY: "scheduleFamilies",
    EXPERIMENT: "experiments",
    CYCLER_TEST: "cyclerTests",
    LAB: "labs",
    TEAM: "teams",
    FILE: "files",
} as const


/**
 * Priority levels govern how visible field information is.
 * IDENTITY fields form part of the resource's display name.
 * CONTEXT fields may be part of the name (e.g. Family name, or Equipment type).
 * SUMMARY fields are shown in the summary view, e.g. cycler test related resources.
 * DETAIL fields are shown in the detail view.
 * Anything with an undefined priority level is assumed to be DETAIL.
 *
 * Special fields may not use the priority system, e.g. Team.
 */
export const PRIORITY_LEVELS = {
    DETAIL: 0,
    SUMMARY: 1,
    CONTEXT: 2,
    IDENTITY: 3
} as const
export type Field = {
    readonly: boolean,
    type: TypeChangerSupportedTypeName,
    many?: boolean,
    priority?: number
}
const always_fields: {[key: string]: Field} = {
    url: {readonly: true, type: "string"},
    permissions: {readonly: true, type: "object"},
}
const generic_fields: {[key: string]: Field} = {
    uuid: {readonly: true, type: "string"},
    ...always_fields,
}

/**
 * Lookup map to get the properties of the fields in each resource type.
 */
export const FIELDS = {
    CYCLER_TEST: {
        ...generic_fields,
        cell: {readonly: false, type: "CELL", priority: PRIORITY_LEVELS.SUMMARY},
        schedule: {readonly: false, type: "SCHEDULE", priority: PRIORITY_LEVELS.SUMMARY},
        equipment: {readonly: false, type: "EQUIPMENT", many: true, priority: PRIORITY_LEVELS.SUMMARY},
        rendered_schedule: {readonly: true, type: "string", many: true},
        team: {readonly: true, type: "TEAM"},
    },
    CELL: {
        ...generic_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        family: {readonly: false, type: "CELL_FAMILY", priority: PRIORITY_LEVELS.CONTEXT},
        team: {readonly: true, type: "TEAM"},
        cycler_tests: {readonly: true, type: "array"},
        in_use: {readonly: true, type: "boolean"},
    },
    EQUIPMENT: {
        ...generic_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        family: {readonly: false, type: "EQUIPIMENT_FAMILY", priority: PRIORITY_LEVELS.CONTEXT},
        team: {readonly: true, type: "TEAM"},
        calibration_date: {readonly: false, type: "string"},
        in_use: {readonly: true, type: "boolean"},
    },
    SCHEDULE: {
        ...generic_fields,
        family: {readonly: false, type: "SCHEDULE_FAMILY", priority: PRIORITY_LEVELS.CONTEXT},
        team: {readonly: true, type: "TEAM"},
        schedule_file: {readonly: false, type: "string"},
        pybamm_schedule_variables: {readonly: false, type: "object"},
    },
    CELL_FAMILY: {
        ...generic_fields,
        manufacturer: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        model: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        form_factor: {readonly: false, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        chemistry: {readonly: false, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        cells: {readonly: true, type: "CELL", many: true, priority: PRIORITY_LEVELS.SUMMARY},
        nominal_voltage: {readonly: false, type: "number"},
        nominal_capacity: {readonly: false, type: "number"},
        initial_ac_impedance: {readonly: false, type: "number"},
        initial_dc_resistance: {readonly: false, type: "number"},
        energy_density: {readonly: false, type: "number"},
        power_density: {readonly: false, type: "number"},
    },
    EQUIPMENT_FAMILY: {
        ...generic_fields,
        manufacturer: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        model: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        type: {readonly: false, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        equipment: {readonly: true, type: "EQUIPMENT", many: true, priority: PRIORITY_LEVELS.SUMMARY},
    },
    SCHEDULE_FAMILY: {
        ...generic_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        ambient_temperature: {readonly: false, type: "number"},
        pybamm_template: {readonly: false, type: "object"},
        schedules: {readonly: true, type: "SCHEDULE", many: true, priority: PRIORITY_LEVELS.SUMMARY},
    },
    TEAM: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        lab: {readonly: true, type: "LAB", priority: PRIORITY_LEVELS.CONTEXT},
        members: {readonly: true, type: "USER", many: true},
        admins: {readonly: true, type: "USER", many: true},
    }
} as const

export type LookupKey = keyof typeof FIELDS

export const has_fields = (maybe_field: any): maybe_field is Field =>
    Object.keys(FIELDS).includes(maybe_field)

/**
 * Names used by the backend to filter by each resource type.
 * E.g. to look up all cells in a cell family, we would filter using
 * the querystring `?family_uuid=uuid`.
 * It is the responsibility of the frontend to ensure that the
 * filter names are employed in the correct context --
 * cell, equipment, and schedule all share the 'family' filter,
 * so the url path must also be appropriate.
 */
export const FILTER_NAMES = {
    CELL_FAMILY: "family_uuid",
    EQUIPMENT_FAMILY: "family_uuid",
    SCHEDULE_FAMILY: "family_uuid",
    CELL: "cell_uuid",
    EQUIPMENT: "equipment_uuid",
    SCHEDULE: "schedule_uuid",
    TEAM: "team_id",
} as const

/**
 * Lookup map to get the family lookup key for each resource type.
 */
export const FAMILY_LOOKUP_KEYS = {
    CELL: "CELL_FAMILY",
    EQUIPMENT: "EQUIPMENT_FAMILY",
    SCHEDULE: "SCHEDULE_FAMILY",
} as const

/**
 * Lookup map to get the child lookup key for each resource family.
 */
export const CHILD_LOOKUP_KEYS = {
    CELL_FAMILY: "CELL",
    EQUIPMENT_FAMILY: "EQUIPMENT",
    SCHEDULE_FAMILY: "SCHEDULE",
} as const

/**
 * Lookup map to get the child field name for each resource family.
 */
export const CHILD_PROPERTY_NAMES  = {
    CELL_FAMILY: "cells",
    EQUIPMENT_FAMILY: "equipment",
    SCHEDULE_FAMILY: "schedules",
} as const
