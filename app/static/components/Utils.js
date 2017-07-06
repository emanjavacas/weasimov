import React from 'react';

// Components
const Spinner = (props) => (
  <div>
    <span className="loading dots"></span>
  </div>);

const Spacer = (props) => <div className="row spacer" style={{height: props.height}}></div>;

function NBSP(props) {
  let nbsp = '&nbsp;';
  for (var i=0; i<props.size; i++) nbsp = nbsp + '&nbsp;';
  return <span dangerouslySetInnerHTML={{__html: nbsp}}></span>;
}


// Utility functions
function getModelData(models, modelName) {
  for (var i=0; i<models.length; i++) {
    if (models[i].path == modelName) return models[i];
  }
  throw Error(`Couldn't find model [${modelName}]`);
};


function timestamp() { return Date.now() / 1000; }


/* Turn model author names into their initials */
function getInitials(name) {
  let title = "Unk";
  if (name) {
    title = "";
    let names = name.split(" ");
    for (var n=0; n<names.length; n++) title += names[n][0];
  }
  return title;
}

function shortenSeed(seed, n){
  if (seed.length > 40) {
    return " ..." + seed.substring(seed.length - n);
  }
  return seed;
}


// AJAX stuff
/**
 * seed: str
 * seed_doc_id: str, current doc id
 * model: str, model path
 * temperature: float
 * max_seq_len: int
 */
function launchGeneration(seed, model, appState, success, error) {
  const {temperature, maxSeqLen, docId} = appState;
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'generate',
    data: JSON.stringify({seed_doc_id: docId,
			  seed: seed,
			  temperature: temperature,
			  model: model,
			  max_seq_len: maxSeqLen}),
    type: 'POST',
    dataType: 'json',
    success: success,
    error: error
  });
}

/**
 * doc_id: str
 * edit: json
 * timestamp: int, unix timestamp
 */
function saveChange(edit, docId) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savechange',
    data: JSON.stringify({edit: edit, timestamp: timestamp(), doc_id: docId}),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}

/**
 * screen_name: str
 * timestamp: int
 */
function createDoc(screenName, success, error) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'createdoc',
    data: JSON.stringify({screen_name: screenName, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => success(response),
    error: (response) => error(response)
  });
}


/**
 * text: json
 * timestamp: int, unix timestamp
 */
function saveDoc(text, docId) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savedoc',
    data: JSON.stringify({text: text, timestamp: timestamp(), doc_id: docId}),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}


/**
 * doc_id: str
 */
function removeDoc(docId, success, error) {
  success = success || console.log;
  error = error || console.log;
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'removedoc',
    data: JSON.stringify({doc_id: docId, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => success(response),
    error: (response) => error(response)
  });
}


/**
 * doc_id: str
 */
function fetchDoc(docId, success, error) {
  success = success || console.log;
  error = error || console.log;
  $.ajax({
    url: 'fetchdoc',
    data: {doc_id: docId},
    type: 'GET',
    dataType: 'json',
    success: (response) => success(response),
    error: (response) => error(response, docId)
  });
}


/**
 * doc_id: str
 * screen_name: str
 * timestamp: int
 */
function editDocName(docId, newName, success, error) {
  success = success || console.log;
  error = error || console.log;
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'editdocname',
    data: JSON.stringify({doc_id: docId, screen_name: newName, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => success(response),
    error: (response) => error(response)
  });
}


/**
 * generation_id: str
 * timestamp: int, unix timestamp
 * doc_id: str, id of currently shown doc
 * selected: True, (optional)
 *   requires:
 *   - draft_entity_id: str
 * dismissed: True, (optional)
 */
function saveSuggestion(generationId, docId, action, draftEntityId) {
  const data = {generation_id: generationId,
		timestamp: timestamp(),
		doc_id: docId};
  if (action === 'selected') {
    data['draft_entity_id'] = draftEntityId;
    data['selected'] = true;
  } else {
    if (action !== 'dismissed')
      throw new Error('Action must be "selected", "dismissed"');
    data['dismissed'] = true;
  }
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savesuggestion',
    data: JSON.stringify(data),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}


/**
 * session: {max_seq_len, temperature}
 */
function saveSession(sessionState) {
  const {temperature, maxSeqLen} = sessionState;
  const session = {"temperature": temperature, "max_seq_len": maxSeqLen};
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: '/savesession',
    type: 'POST',
    dataType: 'json',
    data: JSON.stringify({session}),
    success: (response) => console.log(response.message),
    error: (error) => console.log("Couldn't save session")
  });
}


function init(success, error) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'init',
    type: 'GET',
    dataType: 'json',
    success: (response) => success(response.session),
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


function normalizeDocs(docs) {
  return _arrayToObject(docs, "id");
}


function newDocState(docId, editorState) {
  editorState = editorState || null;
  return {
    docId: docId,	      // docId of the editorState
    editorState: editorState, // actual editor state, it will be null if not loaded yet
    lastEditorState: null,    // last editor state for the doc
    loading: false	      // fetching doc state?
  };
}


function normalizeEditorState(currentDocId, docIds, currentEditorState) {
  const editorStates = docIds.map((docId) => {
    return newDocState(
      docId,
      (docId === currentDocId) ? currentEditorState : null
    );
  });
  return _arrayToObject(editorStates, "docId");
}


const Utils = {
  // components
  Spinner: Spinner,
  Spacer: Spacer,
  NBSP: NBSP,
  // utility functions
  getModelData: getModelData,
  timestamp: timestamp,
  getInitials: getInitials,
  shortenSeed: shortenSeed,
  newDocState: newDocState,
  // ajax
  launchGeneration: launchGeneration,
  saveChange: saveChange,
  saveDoc: saveDoc,
  createDoc: createDoc,
  removeDoc: removeDoc,
  fetchDoc: fetchDoc,
  editDocName: editDocName,
  saveSuggestion: saveSuggestion,
  saveSession: saveSession,
  init: init,
  // normalizers
  normalizeDocs: normalizeDocs,
  normalizeEditorState: normalizeEditorState
};

export default Utils;
