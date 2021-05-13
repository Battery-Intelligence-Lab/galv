import {authFetch} from "./auth"

const url = '/api/'

export async function harvester(id) { 
  if (id) {
    return authFetch(url + `harvester?id=${id}`);
  }
  return authFetch(url + 'harvester');
}

export async function monitored_path(harvester_id) { 
  return authFetch(
    url + `monitored_path?harvester_id=${harvester_id}`
  );
}

