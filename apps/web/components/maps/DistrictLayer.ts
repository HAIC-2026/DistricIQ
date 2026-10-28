import type { Chamber } from "@/types";
export const layers = {
  house: {
    url: "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/33",
    field: "house_id",
    vintage: 2022,
  },
  senate: {
    url: "https://geodata.hawaii.gov/arcgis/rest/services/AdminBnd/MapServer/34",
    field: "senate_id",
    vintage: 2022,
  },
};
export function districtId(chamber: Chamber, number: number) {
  return `${chamber}-${String(number).padStart(2, "0")}`;
}
