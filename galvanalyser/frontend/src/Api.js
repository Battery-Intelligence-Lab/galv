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
