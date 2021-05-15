import {authFetch} from "./auth"

const url = '/api/';
const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    };

export async function harvester(id) { 
  if (id) {
    return authFetch(url + `harvester?id=${id}`);
  }
  return authFetch(url + 'harvester');
}

// path is object with (all optional) fields:
//
// { path: ?, monitored_for: ?, harvester_id: ? }
export async function update_monitored_path(id, path) { 
  return authFetch(
    url + `monitored_path?id=${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(path),
    }
  );
}

// path is object with fields:
//
// { path: ?, monitored_for: ?, harvester_id: ? }
export async function add_monitored_path(path) { 
  return authFetch(
    url + `monitored_path`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(path),
    }
  );
}

export async function del_monitored_path(id) { 
  return authFetch(
    url + `monitored_path?id=${id}`, 
    {
      method: 'DELETE',
    }
  );
}

export async function monitored_path(harvester_id) { 
  return authFetch(
    url + `monitored_path?harvester_id=${harvester_id}`
  );
}

export async function datasets(id) { 
  if (id) {
    return authFetch(url + `dataset?id=${id}`);
  }
  return authFetch(url + 'dataset');

}

