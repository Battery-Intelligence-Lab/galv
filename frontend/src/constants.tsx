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
import AddCircleIcon from '@mui/icons-material/AddCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import CloudSyncIcon from '@mui/icons-material/CloudSync';
import PersonIcon from '@mui/icons-material/Person';

import {
    CellFamiliesApi, CellsApi, CyclerTestsApi, EquipmentApi,
    EquipmentFamiliesApi, ExperimentsApi,
    FilesApi, HarvestersApi, LabsApi,
    ScheduleFamiliesApi, SchedulesApi,
    TeamsApi, UsersApi
} from "./api_codegen";
import {TypeChangerSupportedTypeName} from "./Components/utils/TypeChanger";

/**
 * This is a list of various resources grouped under a common name for each
 * resource type.
 * This allows us to pass a single identifier for the resource type to
 * various components, which can then use this identifier to determine
 * which API to use, which icon to display, etc.
 */
export const LOOKUP_KEYS = {
    HARVESTER: "HARVESTER",
    FILE: "FILE",
    CELL_FAMILY: "CELL_FAMILY",
    EQUIPMENT_FAMILY: "EQUIPMENT_FAMILY",
    SCHEDULE_FAMILY: "SCHEDULE_FAMILY",
    EXPERIMENT: "EXPERIMENT",
    CYCLER_TEST: "CYCLER_TEST",
    CELL: "CELL",
    EQUIPMENT: "EQUIPMENT",
    SCHEDULE: "SCHEDULE",
    LAB: "LAB",
    TEAM: "TEAM",
    USER: "USER"
} as const

export type LookupKey = keyof typeof LOOKUP_KEYS

export const is_lookup_key = (key: any): key is LookupKey => Object.keys(LOOKUP_KEYS).includes(key)

/**
 * Icons for each resource type.
 * Currently all families share the same icon.
 */
export const ICONS = {
    [LOOKUP_KEYS.HARVESTER]: CloudSyncIcon,
    [LOOKUP_KEYS.FILE]: PollIcon,
    [LOOKUP_KEYS.CELL_FAMILY]: BatchPredictionIcon,
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: BatchPredictionIcon,
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: BatchPredictionIcon,
    DASHBOARD: HomeIcon,
    [LOOKUP_KEYS.EXPERIMENT]: DatasetLinkedIcon,
    [LOOKUP_KEYS.CYCLER_TEST]: MultilineChartIcon,
    [LOOKUP_KEYS.CELL]: BatteryFullIcon,
    [LOOKUP_KEYS.EQUIPMENT]: PrecisionManufacturingIcon,
    [LOOKUP_KEYS.SCHEDULE]: AssignmentIcon,
    [LOOKUP_KEYS.LAB]: HolidayVillageIcon,
    [LOOKUP_KEYS.TEAM]: PeopleAltIcon,
    [LOOKUP_KEYS.USER]: PersonIcon,
    CREATE: AddCircleIcon,
    CANCEL: CancelIcon
} as const

/**
 * Paths used by React Router to route to each resource type.
 * This deliberately mimics paths on the API because they are
 * used to determine resource types when parsing URLs that look
 * like they might be resource URLs.
 */
export const PATHS = {
    [LOOKUP_KEYS.HARVESTER]: "/harvesters",
    [LOOKUP_KEYS.FILE]: "/files",
    DASHBOARD: "/",
    [LOOKUP_KEYS.EXPERIMENT]: "/experiments",
    [LOOKUP_KEYS.CYCLER_TEST]: "/cycler_tests",
    DATASET: "/datasets",
    [LOOKUP_KEYS.CELL]: "/cells",
    [LOOKUP_KEYS.CELL_FAMILY]: "/cell_families",
    [LOOKUP_KEYS.EQUIPMENT]: "/equipment",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "/equipment_families",
    [LOOKUP_KEYS.SCHEDULE]: "/schedules",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "/schedule_families",
    [LOOKUP_KEYS.LAB]: "/labs",
    [LOOKUP_KEYS.TEAM]: "/teams",
    [LOOKUP_KEYS.USER]: "/users",
    PROFILE: "/profile",
    TOKEN: "/tokens",
} as const

/**
 * Display names are in Title Case.
 */
export const DISPLAY_NAMES = {
    [LOOKUP_KEYS.HARVESTER]: "Harvester",
    [LOOKUP_KEYS.FILE]: "File",
    DASHBOARD: "Dashboard",
    [LOOKUP_KEYS.EXPERIMENT]: "Experiment",
    [LOOKUP_KEYS.CYCLER_TEST]: "Cycler Test",
    DATASET: "Dataset",
    [LOOKUP_KEYS.CELL]: "Cell",
    [LOOKUP_KEYS.CELL_FAMILY]: "Cell Family",
    [LOOKUP_KEYS.EQUIPMENT]: "Equipment",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "Equipment Family",
    [LOOKUP_KEYS.SCHEDULE]: "Schedule",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "Schedule Family",
    [LOOKUP_KEYS.LAB]: "Lab",
    [LOOKUP_KEYS.TEAM]: "Team",
    [LOOKUP_KEYS.USER]: "User",
    PROFILE: "Profile",
    TOKEN: "Token",
} as const

/**
 * Title Case, as with DISPLAY_NAMES. Plural.
 */
export const DISPLAY_NAMES_PLURAL = {
    [LOOKUP_KEYS.HARVESTER]: "Harvesters",
    [LOOKUP_KEYS.FILE]: "Files",
    DASHBOARD: "Dashboard",
    [LOOKUP_KEYS.EXPERIMENT]: "Experiments",
    [LOOKUP_KEYS.CYCLER_TEST]: "Cycler Tests",
    DATASET: "Datasets",
    [LOOKUP_KEYS.CELL]: "Cells",
    [LOOKUP_KEYS.CELL_FAMILY]: "Cell Families",
    [LOOKUP_KEYS.EQUIPMENT]: "Equipment",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "Equipment Families",
    [LOOKUP_KEYS.SCHEDULE]: "Schedules",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "Schedule Families",
    [LOOKUP_KEYS.LAB]: "Labs",
    [LOOKUP_KEYS.TEAM]: "Teams",
    [LOOKUP_KEYS.USER]: "Users",
    PROFILE: "Profile",
    TOKEN: "Tokens",
} as const

/**
 * API handlers for each resource type.
 * Instantiated with new API_HANDLERS[lookup_key]().
 */
export const API_HANDLERS = {
    [LOOKUP_KEYS.HARVESTER]: HarvestersApi,
    [LOOKUP_KEYS.FILE]: FilesApi,
    [LOOKUP_KEYS.CELL_FAMILY]: CellFamiliesApi,
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: EquipmentFamiliesApi,
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: ScheduleFamiliesApi,
    [LOOKUP_KEYS.EXPERIMENT]: ExperimentsApi,
    [LOOKUP_KEYS.CYCLER_TEST]: CyclerTestsApi,
    [LOOKUP_KEYS.CELL]: CellsApi,
    [LOOKUP_KEYS.EQUIPMENT]: EquipmentApi,
    [LOOKUP_KEYS.SCHEDULE]: SchedulesApi,
    [LOOKUP_KEYS.LAB]: LabsApi,
    [LOOKUP_KEYS.TEAM]: TeamsApi,
    [LOOKUP_KEYS.USER]: UsersApi,
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
    [LOOKUP_KEYS.HARVESTER]: "harvester",
    [LOOKUP_KEYS.FILE]: "files",
    [LOOKUP_KEYS.CELL]: "cells",
    [LOOKUP_KEYS.EQUIPMENT]: "equipment",
    [LOOKUP_KEYS.SCHEDULE]: "schedules",
    [LOOKUP_KEYS.CELL_FAMILY]: "cellFamilies",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "equipmentFamilies",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "scheduleFamilies",
    [LOOKUP_KEYS.EXPERIMENT]: "experiments",
    [LOOKUP_KEYS.CYCLER_TEST]: "cyclerTests",
    [LOOKUP_KEYS.LAB]: "labs",
    [LOOKUP_KEYS.TEAM]: "teams",
    [LOOKUP_KEYS.USER]: "users",
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
    HIDDEN: -1,
    DETAIL: 0,
    SUMMARY: 1,
    CONTEXT: 2,
    IDENTITY: 3
} as const
export type Field = {
    readonly: boolean
    type: TypeChangerSupportedTypeName
    many?: boolean
    priority?: number
    // createonly fields are required at create time, but otherwise readonly
    createonly?: boolean
}
const always_fields: {[key: string]: Field} = {
    url: {readonly: true, type: "string"},
    permissions: {readonly: true, type: "object"},
}
const team_fields: {[key: string]: Field} = {
    team: {readonly: true, type: "TEAM", createonly: true},
}
const generic_fields: {[key: string]: Field} = {
    uuid: {readonly: true, type: "string"},
    ...always_fields,
}

/**
 * Lookup map to get the properties of the fields in each resource type.
 */
export const FIELDS = {
    [LOOKUP_KEYS.HARVESTER]: {
        ...generic_fields,
        name: {readonly: true, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        lab: {readonly: true, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        last_check_in: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        sleep_time: {readonly: true, type: "string"},
        environment_variables: {readonly: true, type: "string"},
        active: {readonly: true, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
    },
    [LOOKUP_KEYS.FILE]: {
        ...generic_fields,
        name: {readonly: true, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        path: {readonly: true, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        harvester: {readonly: true, type: LOOKUP_KEYS.HARVESTER, priority: PRIORITY_LEVELS.CONTEXT},
        last_observed_size: {readonly: true, type: "number"},
        last_observed_time: {readonly: true, type: "string"},
        state: {readonly: true, type: "string"},
        data_generation_date: {readonly: true, type: "string"},
        inferred_format: {readonly: true, type: "string"},
        parser: {readonly: true, type: "string"},
        num_rows: {readonly: true, type: "number"},
        first_sample_no: {readonly: true, type: "number"},
        last_sample_no: {readonly: true, type: "number"},
        extra_metadata: {readonly: true, type: "object"},
        has_required_columns: {readonly: true, type: "boolean", priority: PRIORITY_LEVELS.SUMMARY},
        upload_errors: {readonly: true, type: "string", many: true},
        column_errors: {readonly: true, type: "string", many: true},
        columns: {readonly: true, type: "string", many: true},
    },
    [LOOKUP_KEYS.EXPERIMENT]: {
        title: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        authors: {readonly: false, type: LOOKUP_KEYS.USER, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        protocol: {readonly: true, type: "string"},
        protocol_file: {readonly: true, type: "string"},
        cycler_tests: {readonly: false, type: LOOKUP_KEYS.CYCLER_TEST, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        ...team_fields,
    },
    [LOOKUP_KEYS.CYCLER_TEST]: {
        ...generic_fields,
        cell: {readonly: false, type: LOOKUP_KEYS.CELL, priority: PRIORITY_LEVELS.SUMMARY},
        schedule: {readonly: false, type: LOOKUP_KEYS.SCHEDULE, priority: PRIORITY_LEVELS.SUMMARY},
        equipment: {readonly: false, type: LOOKUP_KEYS.EQUIPMENT, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        rendered_schedule: {readonly: true, type: "string", many: true},
        ...team_fields,
    },
    [LOOKUP_KEYS.CELL]: {
        ...generic_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        family: {readonly: false, type: LOOKUP_KEYS.CELL_FAMILY, priority: PRIORITY_LEVELS.CONTEXT},
        ...team_fields,
        cycler_tests: {readonly: true, type: "array"},
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.EQUIPMENT]: {
        ...generic_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        family: {readonly: false, type: LOOKUP_KEYS.EQUIPMENT_FAMILY, priority: PRIORITY_LEVELS.CONTEXT},
        ...team_fields,
        calibration_date: {readonly: false, type: "string"},
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.SCHEDULE]: {
        ...generic_fields,
        family: {readonly: false, type: LOOKUP_KEYS.SCHEDULE_FAMILY, priority: PRIORITY_LEVELS.CONTEXT},
        ...team_fields,
        schedule_file: {readonly: false, type: "string"},
        pybamm_schedule_variables: {readonly: false, type: "object"},
    },
    [LOOKUP_KEYS.CELL_FAMILY]: {
        ...generic_fields,
        ...team_fields,
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
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: {
        ...generic_fields,
        ...team_fields,
        manufacturer: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        model: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        type: {readonly: false, type: "string", priority: PRIORITY_LEVELS.CONTEXT},
        equipment: {readonly: true, type: LOOKUP_KEYS.EQUIPMENT, many: true, priority: PRIORITY_LEVELS.SUMMARY},
    },
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: {
        ...generic_fields,
        ...team_fields,
        identifier: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        ambient_temperature: {readonly: false, type: "number"},
        pybamm_template: {readonly: false, type: "object"},
        schedules: {readonly: true, type: LOOKUP_KEYS.SCHEDULE, many: true, priority: PRIORITY_LEVELS.SUMMARY},
    },
    [LOOKUP_KEYS.TEAM]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        lab: {readonly: true, type: LOOKUP_KEYS.LAB, priority: PRIORITY_LEVELS.CONTEXT},
        members: {readonly: true, type: LOOKUP_KEYS.USER, many: true},
        admins: {readonly: true, type: LOOKUP_KEYS.USER, many: true},
    },
    [LOOKUP_KEYS.LAB]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        admin_group: {readonly: true, type: LOOKUP_KEYS.USER, many: true},
        teams: {readonly: true, type: LOOKUP_KEYS.TEAM, many: true},
    },
    [LOOKUP_KEYS.USER]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        username: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        email: {readonly: false, type: "string"},
        first_name: {readonly: false, type: "string"},
        last_name: {readonly: false, type: "string"},
    }
} as const

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
    [LOOKUP_KEYS.CELL_FAMILY]: "family_uuid",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "family_uuid",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "family_uuid",
    [LOOKUP_KEYS.CELL]: "cell_uuid",
    [LOOKUP_KEYS.EQUIPMENT]: "equipment_uuid",
    [LOOKUP_KEYS.SCHEDULE]: "schedule_uuid",
    [LOOKUP_KEYS.TEAM]: "team_id",
} as const

/**
 * Lookup map to get the family lookup key for each resource type.
 */
export const FAMILY_LOOKUP_KEYS = {
    [LOOKUP_KEYS.CELL]: "CELL_FAMILY",
    [LOOKUP_KEYS.EQUIPMENT]: "EQUIPMENT_FAMILY",
    [LOOKUP_KEYS.SCHEDULE]: "SCHEDULE_FAMILY",
} as const

export const get_has_family = (key: string|number): key is keyof typeof FAMILY_LOOKUP_KEYS =>
    Object.keys(FAMILY_LOOKUP_KEYS).includes(key as string)
/**
 * Lookup map to get the child lookup key for each resource family.
 */
export const CHILD_LOOKUP_KEYS = {
    [LOOKUP_KEYS.CELL_FAMILY]: "CELL",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "EQUIPMENT",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "SCHEDULE",
} as const

/**
 * Lookup map to get the child field name for each resource family.
 */
export const CHILD_PROPERTY_NAMES  = {
    [LOOKUP_KEYS.CELL_FAMILY]: "cells",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "equipment",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "schedules",
} as const

export const get_is_family = (key: string|number): key is keyof typeof CHILD_PROPERTY_NAMES =>
    Object.keys(CHILD_PROPERTY_NAMES).includes(key as string)