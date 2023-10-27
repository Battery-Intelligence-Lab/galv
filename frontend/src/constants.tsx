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
import AttachFileIcon from '@mui/icons-material/AttachFile';
import {OverridableComponent} from "@mui/material/OverridableComponent";
import {SvgIconTypeMap} from "@mui/material";
import {
    CellFamiliesApi, CellsApi, CyclerTestsApi, EquipmentApi,
    EquipmentFamiliesApi, ExperimentsApi,
    FilesApi, LabsApi,
    ScheduleFamiliesApi, SchedulesApi,
    TeamsApi
} from "./api_codegen";

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

const _get_representation_factory = (fun: (i: any) => string) => {
    return (instance: any) => {
        try {
            return fun(instance)
        } catch (e) {
            if (instance === undefined) return "[undefined]"
            console.error(`Could not get representation for ${instance}`, e)
            return instance.toString()
        }
    }
}

/**
 * Representation functions to present each resource family in a human-readable
 * format.
 */
export const GET_REPRESENTATIONS = {
    CELL_FAMILY: _get_representation_factory(
        (instance: any) => `${instance.manufacturer} ${instance.model} [${instance.form_factor} ${instance.chemistry}]`
    ),
    EQUIPMENT_FAMILY: _get_representation_factory(
        (instance: any) => `${instance.type} ${instance.manufacturer} ${instance.model} [${instance.type}]`
    ),
    SCHEDULE_FAMILY: _get_representation_factory(
        (instance: any) => `${instance.identifier}`
    ),
}