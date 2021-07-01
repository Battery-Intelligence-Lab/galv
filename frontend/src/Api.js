
const url = '/api/';
const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    };

export async function login(username, password) {
  let headers = new Headers();
  headers.set('Authorization', 'Basic ' + btoa(username + ":" + password));
  return fetch(url + '/login', {method: 'POST', headers: headers});
}

export async function logout() {
  return fetch(url + '/logout', {method: 'POST'});
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

export function loggedIn() {
  const cookie = getCookie('csrf_access_token');
  return  cookie !== undefined;
}

async function authFetch(url, options) {
  let newOptions = {...options};
  newOptions.credentials = 'same-origin';
  newOptions.headers = {...newOptions.headers};
  newOptions.headers['X-CSRF-TOKEN'] = getCookie('csrf_access_token');
  return fetch(url, newOptions).then((response) => {
    if (response.status === 401) {
      return logout().then(() => {
        return response;
      });
    }
    return response;
  });;
}

export async function run_harvester(id) { 
  return authFetch(
    url + `harvester/${id}/run`,
    {
      method: 'PUT',
      headers: headers,
    }
  );
}

export async function env_harvester(id) { 
  return authFetch(url + `harvester/${id}/env`);
}

export async function harvesters(id) { 
  if (id) {
    return authFetch(url + `harvester/${id}`);
  }
  return authFetch(url + 'harvester');
}

export async function delete_harvester(id) { 
  return authFetch(
    url + `harvester/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

// harvester is object with fields:
//
// { machine_id: ? }
export async function add_harvester(harvester) { 
  return authFetch(
    url + `harvester`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(harvester),
    }
  );
}

// harvester is object with fields:
//
// { machine_id: ? }
export async function update_harvester(id, harvester) { 
  return authFetch(
    url + `harvester/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(harvester),
    }
  );
}

// path is object with (all optional) fields:
//
// { path: ?, monitored_for: ?, harvester_id: ? }
export async function update_monitored_path(id, path) { 
  return authFetch(
    url + `monitored_path/${id}`, 
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

export async function delete_monitored_path(id) { 
  return authFetch(
    url + `monitored_path/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

export async function monitored_paths(harvester_id) { 
  return authFetch(
    url + `monitored_path?harvester_id=${harvester_id}`
  );
}

export async function users() { 
  return authFetch(url + 'user');
}

export async function files(path_id) { 
  return authFetch(url + `file?path_id=${path_id}`);
}

export async function datasets(id) { 
  if (id) {
    return authFetch(url + `dataset/${id}`);
  }
  return authFetch(url + 'dataset');

}

// dataset is object with fields:
//
// { name: ?, cell_id: ?, 
//   owner: ?, test_equipment: ?, 
//   purpose: ? }
export async function update_dataset(id, dataset) { 
  return authFetch(
    url + `dataset/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(dataset),
    }
  );
}

export async function metadata(dataset_id) { 
  return authFetch(url + `metadata/${dataset_id}`);
}

export async function equipment(id) { 
  if (id) {
    return authFetch(url + `equipment/${id}`);
  }
  return authFetch(url + `equipment`);
}

//// equipment is object with fields:
//
// { name: ?, type: ?, }
export async function add_equipment(equipment) { 
  return authFetch(
    url + `equipment`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(equipment),
    }
  );
}

// equipment is object with fields:
//
// { name: ?, type: ?, }
export async function update_equipment(id, equipment) { 
  return authFetch(
    url + `equipment/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(equipment),
    }
  );
}

export async function delete_equipment(id) { 
  return authFetch(
    url + `equipment/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

export async function cells(id) { 
  if (id) {
    return authFetch(url + `cell/${id}`);
  }
  return authFetch(url + `cell`);
}

//// cell is object with fields:
//
// { cell_form_factor: ?, link_to_datasheet: ?, 
//   anode_chemistry: ?, cathode_chemistry: ?, 
//   nominal_capacity: ?, nominal_cell_weight: ? }
export async function add_cell(cell) { 
  return authFetch(
    url + `cell`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(cell),
    }
  );
}

// cell is object with fields:
//
// { cell_form_factor: ?, link_to_datasheet: ?, 
//   anode_chemistry: ?, cathode_chemistry: ?, 
//   nominal_capacity: ?, nominal_cell_weight: ? }
export async function update_cell(id, cell) { 
  return authFetch(
    url + `cell/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(cell),
    }
  );
}

export async function delete_cell(id) { 
  return authFetch(
    url + `cell/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

export async function manufacturers(id) { 
  if (id) {
    return authFetch(url + `manufacturer/${id}`);
  }
  return authFetch(url + `manufacturer`);
}

export async function delete_manufacturer(id) { 
  return authFetch(
    url + `manufacturer/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

// manufacturer is object with fields:
//
// { name: ? }
export async function add_manufacturer(manufacturer) { 
  return authFetch(
    url + `manufacturer`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(manufacturer),
    }
  );
}

// cell is object with fields:
//
// { path: ?, monitored_for: ?, harvester_id: ? }
export async function update_manufacturer(id, manufacturer) { 
  return authFetch(
    url + `manufacturer/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(manufacturer),
    }
  );
}

export async function institutions(id) { 
  if (id) {
    return authFetch(url + `institution/${id}`);
  }
  return authFetch(url + `institution`);
}

export async function delete_institution(id) { 
  return authFetch(
    url + `institution/${id}`, 
    {
      method: 'DELETE',
    }
  );
}

// institution is object with fields:
//
// { name: ? }
export async function add_institution(institution) { 
  return authFetch(
    url + `institution`, 
    {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(institution),
    }
  );
}

// manufactureris object with fields:
//
// { path: ?, monitored_for: ?, harvester_id: ? }
export async function update_institution(id, institution) { 
  return authFetch(
    url + `institution/${id}`, 
    {
      method: 'PUT',
      headers: headers,
      body: JSON.stringify(institution),
    }
  );
}

export async function add_metadata(dataset_id) { 
  return authFetch(
    url + `metadata/${dataset_id}`, 
    {
      method: 'POST',
    }
  );
}

// metadata is object with fields:
//
// { cell_uid: ?, json_data: ?, owner: ?, purpose: ?, test_equipment: ? }
export async function update_metadata(dataset_id, metadata) { 
  return authFetch(
    url + `metadata/${dataset_id}`, 
    {
      method: 'PUT',
      body: JSON.stringify(metadata),
    }
  );
}

export async function columns(dataset_id) { 
  return authFetch(url + `column?dataset_id=${dataset_id}`);
}

export async function timeseries_column(dataset_id, col_id) { 
  return authFetch(url + `dataset/${dataset_id}/${col_id}`,
    {
      responseType: 'arraybuffer',
      headers: {
        'Accept': 'application/octet-stream'
      }
    }
  ).then((response) => {
   if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.arrayBuffer();
  }).then((buffer) => {
    const floats = new Float32Array(buffer);
    return floats;
  });
}
