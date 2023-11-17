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
import FolderIcon from '@mui/icons-material/Folder';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import ManageAccountsIcon from '@mui/icons-material/ManageAccounts';
import LogoutIcon from '@mui/icons-material/Logout';
import SchemaIcon from '@mui/icons-material/Schema';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';
import ErrorIcon from '@mui/icons-material/Error';
import HideSourceIcon from '@mui/icons-material/HideSource';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import DownloadIcon from '@mui/icons-material/Download';

import {
    CellChemistriesApi,
    CellFamiliesApi, CellFormFactorsApi, CellManufacturersApi, CellModelsApi, CellsApi, CyclerTestsApi, EquipmentApi,
    EquipmentFamiliesApi, EquipmentManufacturersApi, EquipmentModelsApi, EquipmentTypesApi, ExperimentsApi,
    FilesApi, HarvestersApi, LabsApi, MonitoredPathsApi,
    ScheduleFamiliesApi, ScheduleIdentifiersApi, SchedulesApi,
    TeamsApi, TokensApi, UsersApi, ValidationSchemasApi
} from "./api_codegen";
import {Serializable, TypeChangerSupportedTypeName} from "./Components/TypeChanger";

/**
 * This is a list of various resources grouped under a common name for each
 * resource type.
 * This allows us to pass a single identifier for the resource type to
 * various components, which can then use this identifier to determine
 * which API to use, which icon to display, etc.
 *
 * TODO: Eventually these could all be exposed as part of a useLookupKey context.
 */
export const LOOKUP_KEYS = {
    HARVESTER: "HARVESTER",
    PATH: "PATH",
    FILE: "FILE",
    CELL_FAMILY: "CELL_FAMILY",
    CELL: "CELL",
    EQUIPMENT_FAMILY: "EQUIPMENT_FAMILY",
    EQUIPMENT: "EQUIPMENT",
    SCHEDULE_FAMILY: "SCHEDULE_FAMILY",
    SCHEDULE: "SCHEDULE",
    EXPERIMENT: "EXPERIMENT",
    CYCLER_TEST: "CYCLER_TEST",
    VALIDATION_SCHEMA: "VALIDATION_SCHEMA",
    LAB: "LAB",
    TEAM: "TEAM",
    USER: "USER",
    TOKEN: "TOKEN",
} as const

export const AUTOCOMPLETE_KEYS = {
    CELL_MANUFACTURER: "CELL_MANUFACTURER",
    CELL_MODEL: "CELL_MODEL",
    CELL_FORM_FACTOR: "CELL_FORM_FACTOR",
    CELL_CHEMISTRY: "CELL_CHEMISTRY",
    EQUIPMENT_TYPE: "EQUIPMENT_TYPE",
    EQUIPMENT_MANUFACTURER: "EQUIPMENT_MANUFACTURER",
    EQUIPMENT_MODEL: "EQUIPMENT_MODEL",
    SCHEDULE_IDENTIFIER: "SCHEDULE_IDENTIFIER",
} as const

export type LookupKey = keyof typeof LOOKUP_KEYS
export const is_lookup_key = (key: any): key is LookupKey => Object.keys(LOOKUP_KEYS).includes(key)

export type AutocompleteKey = keyof typeof AUTOCOMPLETE_KEYS
export const is_autocomplete_key = (key: any): key is AutocompleteKey => Object.keys(AUTOCOMPLETE_KEYS).includes(key)

/**
 * Icons for each resource type.
 * Currently all families share the same icon.
 */
export const ICONS = {
    [LOOKUP_KEYS.HARVESTER]: CloudSyncIcon,
    [LOOKUP_KEYS.PATH]: FolderIcon,
    [LOOKUP_KEYS.FILE]: PollIcon,
    [LOOKUP_KEYS.CELL_FAMILY]: BatchPredictionIcon,
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: BatchPredictionIcon,
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: BatchPredictionIcon,
    [LOOKUP_KEYS.EXPERIMENT]: DatasetLinkedIcon,
    [LOOKUP_KEYS.CYCLER_TEST]: MultilineChartIcon,
    [LOOKUP_KEYS.CELL]: BatteryFullIcon,
    [LOOKUP_KEYS.EQUIPMENT]: PrecisionManufacturingIcon,
    [LOOKUP_KEYS.SCHEDULE]: AssignmentIcon,
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: SchemaIcon,
    [LOOKUP_KEYS.LAB]: HolidayVillageIcon,
    [LOOKUP_KEYS.TEAM]: PeopleAltIcon,
    [LOOKUP_KEYS.USER]: PersonIcon,
    [LOOKUP_KEYS.TOKEN]: VpnKeyIcon,
    DASHBOARD: HomeIcon,
    MANAGE_ACCOUNT: ManageAccountsIcon,
    LOGOUT: LogoutIcon,
    CREATE: AddCircleIcon,
    CANCEL: CancelIcon,
    CHECK: CheckCircleIcon,
    EXPAND_MORE: ExpandMoreIcon,
    EXPAND_LESS: ExpandLessIcon,
    DOWNLOAD: DownloadIcon,
    validation_status_ERROR: ErrorIcon,
    validation_status_UNCHECKED: PendingIcon,
    validation_status_VALID: CheckCircleIcon,
    validation_status_INVALID: CancelIcon,
    validation_status_SKIPPED: HideSourceIcon,
} as const

/**
 * Paths used by React Router to route to each resource type.
 * This deliberately mimics paths on the API because they are
 * used to determine resource types when parsing URLs that look
 * like they might be resource URLs.
 */
export const PATHS = {
    [LOOKUP_KEYS.HARVESTER]: "/harvesters",
    [LOOKUP_KEYS.PATH]: "/paths",
    [LOOKUP_KEYS.FILE]: "/files",
    DASHBOARD: "/",
    [LOOKUP_KEYS.EXPERIMENT]: "/experiments",
    [LOOKUP_KEYS.CYCLER_TEST]: "/cycler_tests",
    GRAPH: "/graphs",
    [LOOKUP_KEYS.CELL]: "/cells",
    [LOOKUP_KEYS.CELL_FAMILY]: "/cell_families",
    [LOOKUP_KEYS.EQUIPMENT]: "/equipment",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "/equipment_families",
    [LOOKUP_KEYS.SCHEDULE]: "/schedules",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "/schedule_families",
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: "/validation_schemas",
    [LOOKUP_KEYS.LAB]: "/labs",
    [LOOKUP_KEYS.TEAM]: "/teams",
    [LOOKUP_KEYS.USER]: "/users",
    [LOOKUP_KEYS.TOKEN]: "/tokens",
    PROFILE: "/profile",
} as const

/**
 * Display names are in Title Case.
 */
export const DISPLAY_NAMES = {
    [LOOKUP_KEYS.HARVESTER]: "Harvester",
    [LOOKUP_KEYS.PATH]: "Path",
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
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: "Validation Schema",
    [LOOKUP_KEYS.LAB]: "Lab",
    [LOOKUP_KEYS.TEAM]: "Team",
    [LOOKUP_KEYS.USER]: "User",
    [LOOKUP_KEYS.TOKEN]: "Token",
} as const

/**
 * Title Case, as with DISPLAY_NAMES. Plural.
 */
export const DISPLAY_NAMES_PLURAL = {
    [LOOKUP_KEYS.HARVESTER]: "Harvesters",
    [LOOKUP_KEYS.PATH]: "Paths",
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
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: "Validation Schemas",
    [LOOKUP_KEYS.LAB]: "Labs",
    [LOOKUP_KEYS.TEAM]: "Teams",
    [LOOKUP_KEYS.USER]: "Users",
    [LOOKUP_KEYS.TOKEN]: "Tokens",
} as const

/**
 * API handlers for each resource type.
 * Instantiated with new API_HANDLERS[lookup_key]().
 */
export const API_HANDLERS = {
    [LOOKUP_KEYS.HARVESTER]: HarvestersApi,
    [LOOKUP_KEYS.PATH]: MonitoredPathsApi,
    [LOOKUP_KEYS.FILE]: FilesApi,
    [LOOKUP_KEYS.CELL_FAMILY]: CellFamiliesApi,
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: EquipmentFamiliesApi,
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: ScheduleFamiliesApi,
    [LOOKUP_KEYS.EXPERIMENT]: ExperimentsApi,
    [LOOKUP_KEYS.CYCLER_TEST]: CyclerTestsApi,
    [LOOKUP_KEYS.CELL]: CellsApi,
    [LOOKUP_KEYS.EQUIPMENT]: EquipmentApi,
    [LOOKUP_KEYS.SCHEDULE]: SchedulesApi,
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: ValidationSchemasApi,
    [LOOKUP_KEYS.LAB]: LabsApi,
    [LOOKUP_KEYS.TEAM]: TeamsApi,
    [LOOKUP_KEYS.USER]: UsersApi,
    [LOOKUP_KEYS.TOKEN]: TokensApi,
    [AUTOCOMPLETE_KEYS.CELL_MANUFACTURER]: CellManufacturersApi,
    [AUTOCOMPLETE_KEYS.CELL_MODEL]: CellModelsApi,
    [AUTOCOMPLETE_KEYS.CELL_FORM_FACTOR]: CellFormFactorsApi,
    [AUTOCOMPLETE_KEYS.CELL_CHEMISTRY]: CellChemistriesApi,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_TYPE]: EquipmentTypesApi,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MANUFACTURER]: EquipmentManufacturersApi,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MODEL]: EquipmentModelsApi,
    [AUTOCOMPLETE_KEYS.SCHEDULE_IDENTIFIER]: ScheduleIdentifiersApi,
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
    [LOOKUP_KEYS.HARVESTER]: "harvesters",
    [LOOKUP_KEYS.PATH]: "monitoredPaths",
    [LOOKUP_KEYS.FILE]: "files",
    [LOOKUP_KEYS.CELL]: "cells",
    [LOOKUP_KEYS.EQUIPMENT]: "equipment",
    [LOOKUP_KEYS.SCHEDULE]: "schedules",
    [LOOKUP_KEYS.CELL_FAMILY]: "cellFamilies",
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: "equipmentFamilies",
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: "scheduleFamilies",
    [LOOKUP_KEYS.EXPERIMENT]: "experiments",
    [LOOKUP_KEYS.CYCLER_TEST]: "cyclerTests",
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: "validationSchemas",
    [LOOKUP_KEYS.LAB]: "labs",
    [LOOKUP_KEYS.TEAM]: "teams",
    [LOOKUP_KEYS.USER]: "users",
    [LOOKUP_KEYS.TOKEN]: "tokens",
    [AUTOCOMPLETE_KEYS.CELL_MANUFACTURER]: "cellManufacturers",
    [AUTOCOMPLETE_KEYS.CELL_MODEL]: "cellModels",
    [AUTOCOMPLETE_KEYS.CELL_FORM_FACTOR]: "cellFormFactors",
    [AUTOCOMPLETE_KEYS.CELL_CHEMISTRY]: "cellChemistries",
    [AUTOCOMPLETE_KEYS.EQUIPMENT_TYPE]: "equipmentTypes",
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MANUFACTURER]: "equipmentManufacturers",
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MODEL]: "equipmentModels",
    [AUTOCOMPLETE_KEYS.SCHEDULE_IDENTIFIER]: "scheduleIdentifiers",
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
    // If field data need transforming from API to frontend, provide a function here.
    // It is called in ApiResourceContextProvider, and may be called multiple times,
    // so it should handle receiving already transformed data.
    transformation?: (d: Serializable) => Serializable
}
const always_fields: {[key: string]: Field} = {
    url: {readonly: true, type: "string"},
    permissions: {readonly: true, type: "object"},
}
const team_fields: {[key: string]: Field} = {
    team: {readonly: true, type: "TEAM", createonly: true},
    validation_results: {readonly: true, type: "object", many: true},
}
const generic_fields: {[key: string]: Field} = {
    uuid: {readonly: true, type: "string"},
    ...always_fields,
}
const autocomplete_fields: {[key: string]: Field} = {
    url: {readonly: true, type: "string"},
    id: {readonly: true, type: "number"},
    value: {readonly: true, type: "string"},
    ld_value: {readonly: true, type: "string"},
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
    [LOOKUP_KEYS.PATH]: {
        ...generic_fields,
        path: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        regex: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        stable_time: {readonly: false, type: "number"},
        active: {readonly: false, type: "boolean", priority: PRIORITY_LEVELS.SUMMARY},
        harvester: {
            readonly: true,
            type: LOOKUP_KEYS.HARVESTER,
            priority: PRIORITY_LEVELS.CONTEXT,
            createonly: true
        },
        files: {readonly: true, type: LOOKUP_KEYS.FILE, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        ...team_fields,
    },
    [LOOKUP_KEYS.FILE]: {
        ...generic_fields,
        name: {readonly: true, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        state: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        path: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        parser: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        harvester: {readonly: true, type: LOOKUP_KEYS.HARVESTER, priority: PRIORITY_LEVELS.CONTEXT},
        last_observed_size: {readonly: true, type: "number"},
        last_observed_time: {readonly: true, type: "string"},
        data_generation_date: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        inferred_format: {readonly: true, type: "string"},
        num_rows: {readonly: true, type: "number"},
        first_sample_no: {readonly: true, type: "number"},
        last_sample_no: {readonly: true, type: "number"},
        extra_metadata: {readonly: true, type: "object"},
        has_required_columns: {readonly: true, type: "boolean", priority: PRIORITY_LEVELS.SUMMARY},
        upload_errors: {readonly: true, type: "string", many: true},
        column_errors: {readonly: true, type: "string", many: true},
        columns: {readonly: true, type: "string", many: true},
        upload_info: {readonly: true, type: "string"},
    },
    [LOOKUP_KEYS.EXPERIMENT]: {
        title: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        authors: {readonly: false, type: LOOKUP_KEYS.USER, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        protocol: {readonly: true, type: "string"},
        protocol_file: {readonly: true, type: "string"},
        cycler_tests: {readonly: true, type: LOOKUP_KEYS.CYCLER_TEST, many: true, priority: PRIORITY_LEVELS.SUMMARY},
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
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.CELL_FAMILY]: {
        ...generic_fields,
        ...team_fields,
        manufacturer: {readonly: false, type: AUTOCOMPLETE_KEYS.CELL_MANUFACTURER, priority: PRIORITY_LEVELS.IDENTITY},
        model: {readonly: false, type: AUTOCOMPLETE_KEYS.CELL_MODEL, priority: PRIORITY_LEVELS.IDENTITY},
        form_factor: {readonly: false, type: AUTOCOMPLETE_KEYS.CELL_FORM_FACTOR, priority: PRIORITY_LEVELS.CONTEXT},
        chemistry: {readonly: false, type: AUTOCOMPLETE_KEYS.CELL_CHEMISTRY, priority: PRIORITY_LEVELS.CONTEXT},
        cells: {readonly: true, type: "CELL", many: true, priority: PRIORITY_LEVELS.SUMMARY},
        nominal_voltage: {readonly: false, type: "number"},
        nominal_capacity: {readonly: false, type: "number"},
        initial_ac_impedance: {readonly: false, type: "number"},
        initial_dc_resistance: {readonly: false, type: "number"},
        energy_density: {readonly: false, type: "number"},
        power_density: {readonly: false, type: "number"},
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.EQUIPMENT_FAMILY]: {
        ...generic_fields,
        ...team_fields,
        manufacturer: {readonly: false, type: AUTOCOMPLETE_KEYS.EQUIPMENT_MANUFACTURER, priority: PRIORITY_LEVELS.IDENTITY},
        model: {readonly: false, type: AUTOCOMPLETE_KEYS.EQUIPMENT_MODEL, priority: PRIORITY_LEVELS.IDENTITY},
        type: {readonly: false, type: AUTOCOMPLETE_KEYS.EQUIPMENT_TYPE, priority: PRIORITY_LEVELS.CONTEXT},
        equipment: {readonly: true, type: LOOKUP_KEYS.EQUIPMENT, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.SCHEDULE_FAMILY]: {
        ...generic_fields,
        ...team_fields,
        identifier: {readonly: false, type: AUTOCOMPLETE_KEYS.SCHEDULE_IDENTIFIER, priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string"},
        ambient_temperature: {readonly: false, type: "number"},
        pybamm_template: {readonly: false, type: "object"},
        schedules: {readonly: true, type: LOOKUP_KEYS.SCHEDULE, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        in_use: {readonly: true, type: "boolean"},
    },
    [LOOKUP_KEYS.TEAM]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        lab: {readonly: true, type: LOOKUP_KEYS.LAB, priority: PRIORITY_LEVELS.CONTEXT},
        member_group: {
            readonly: true,
            type: LOOKUP_KEYS.USER,
            many: true,
            priority: PRIORITY_LEVELS.SUMMARY,
            transformation: (group: any) => group?.users ?? group ?? []
        },
        admin_group: {
            readonly: true,
            type: LOOKUP_KEYS.USER,
            many: true,
            priority: PRIORITY_LEVELS.SUMMARY,
            transformation: (group: any) => group?.users ?? group ?? []
        },
        monitored_paths: {readonly: true, type: LOOKUP_KEYS.PATH, many: true},
        cellfamily_resources: {readonly: true, type: LOOKUP_KEYS.CELL_FAMILY, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        cell_resources: {readonly: true, type: LOOKUP_KEYS.CELL, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        equipmentfamily_resources: {readonly: true, type: LOOKUP_KEYS.EQUIPMENT_FAMILY, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        equipment_resources: {readonly: true, type: LOOKUP_KEYS.EQUIPMENT, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        schedulefamily_resources: {readonly: true, type: LOOKUP_KEYS.SCHEDULE_FAMILY, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        schedule_resources: {readonly: true, type: LOOKUP_KEYS.SCHEDULE, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        cyclertest_resources: {readonly: true, type: LOOKUP_KEYS.CYCLER_TEST, many: true, priority: PRIORITY_LEVELS.CONTEXT},
        experiment_resources: {readonly: true, type: LOOKUP_KEYS.EXPERIMENT, many: true, priority: PRIORITY_LEVELS.CONTEXT},
    },
    [LOOKUP_KEYS.VALIDATION_SCHEMA]: {
        ...generic_fields,
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        schema: {readonly: false, type: "object"},
        ...team_fields,
    },
    [LOOKUP_KEYS.LAB]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        description: {readonly: false, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
        admin_group: {
            readonly: true,
            type: LOOKUP_KEYS.USER,
            many: true,
            transformation: (group: any) => group?.users ?? group ?? [],
            priority: PRIORITY_LEVELS.SUMMARY
        },
        teams: {readonly: true, type: LOOKUP_KEYS.TEAM, many: true, priority: PRIORITY_LEVELS.SUMMARY},
        harvesters: {readonly: true, type: LOOKUP_KEYS.HARVESTER, many: true, priority: PRIORITY_LEVELS.SUMMARY},
    },
    [LOOKUP_KEYS.USER]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        username: {readonly: false, type: "string", priority: PRIORITY_LEVELS.IDENTITY},
        email: {readonly: false, type: "string"},
        first_name: {readonly: false, type: "string"},
        last_name: {readonly: false, type: "string"},
        is_staff: {readonly: true, type: "boolean", priority: PRIORITY_LEVELS.HIDDEN},
        is_superuser: {readonly: true, type: "boolean"},
        groups: {readonly: true, type: "object", many: true, priority: PRIORITY_LEVELS.HIDDEN},
    },
    [LOOKUP_KEYS.TOKEN]: {
        ...always_fields,
        id: {readonly: true, type: "number"},
        name: {readonly: true, type: "string", createonly: true, priority: PRIORITY_LEVELS.IDENTITY},
        created: {readonly: true, type: "string"},
        expiry: {readonly: true, type: "string", priority: PRIORITY_LEVELS.SUMMARY},
    },
    [AUTOCOMPLETE_KEYS.CELL_MANUFACTURER]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.CELL_MODEL]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.CELL_FORM_FACTOR]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.CELL_CHEMISTRY]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_TYPE]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MANUFACTURER]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.EQUIPMENT_MODEL]: autocomplete_fields,
    [AUTOCOMPLETE_KEYS.SCHEDULE_IDENTIFIER]: autocomplete_fields,
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