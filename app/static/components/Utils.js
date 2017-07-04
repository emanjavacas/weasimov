import React from 'react';

// Components
const Spinner = (props) => (
  <div>
    <span className="loading dots"></span>
  </div>);

const Spacer = (props) => <div className="row" style={{height: props.height}}></div>;

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
    let names = name.split(" ");
    for (var n=0; n<names.length; n++) title += names[n][0];
  }
  return title;
}

function shortenSeed(seed, n){
  if (seed.length > 40) {
    return seed.substring(-1, n) + " ...";
  }
  return seed;
}


// AJAX stuff
function launchGeneration(seed, model, appState, success, error) {
  const {temperature, maxSeqLen} = appState;
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'generate',
    data: JSON.stringify(
      {'selection': seed,
       'temperature': temperature,
       'model_path': model,
       'max_seq_len': maxSeqLen}),
    type: 'POST',
    dataType: 'json',
    success: success,
    error: error
  });
}

/**
 * edit: json
 * timestamp: int, unix timestamp
 */
function saveChange(edit) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savechange',
    data: JSON.stringify({edit: edit, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}


/**
 * text: json
 * timestamp: int, unix timestamp
 */
function saveDoc(text) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savedoc',
    data: JSON.stringify({text: text, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}


/**
 * generation_id: str
 * draft_entity_id: str
 * timestamp: int, unix timestamp
 */
function saveSuggestion(generation_id, draft_entity_id) {
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: 'savesuggestion',
    data: JSON.stringify({generation_id, draft_entity_id, timestamp: timestamp()}),
    type: 'POST',
    dataType: 'json',
    success: (response) => console.log(response),
    error: (error) => console.log(error)
  });
}


/**
 * session: {max_seq_len, temperature, hyps}
 */
function saveSession(state) {
  const {temperature, maxSeqLen} = state;
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
  // ajax
  launchGeneration: launchGeneration,
  saveChange: saveChange,
  saveDoc: saveDoc,
  saveSuggestion: saveSuggestion,
  saveSession: saveSession,
  init: init
};

export default Utils;
