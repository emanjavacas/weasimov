
// AJAX
function monitorInit(success, error) {
  $.ajax({
    url: 'monitorinit',
    type: 'GET',
    dataType: 'json',
    success: success,
    error: error
  });
}


// Normalizers
function _arrayToObject(array, fieldId) {
  let newObj = {};
  for (var i=0; i<array.length; i++) {
    const obj = array[i];
    newObj[obj[fieldId]] = obj;
  }
  return newObj;
}


function normalizeUsers(users) {
  return _arrayToObject(users, "id"); 
}


function normalizeDocs(docs) {
  return _arrayToObject(docs, "id");
}


function filterDocs(docs, userId) {
  const result = {};
  const docIds = Object.keys(docs);
  for (var i=0; i<docIds.length; i++) {
    let docId = docIds[i];
    if (docs[docId].user_id === userId) {
      result[docId] = docs[docId];
    }
  }
  return result;
}


const MonitorUtils = {
  // ajax
  monitorInit: monitorInit,
  // normalizers
  normalizeUsers: normalizeUsers,
  normalizeDocs: normalizeDocs,
  // utility
  filterDocs: filterDocs
};


export default MonitorUtils;
