import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, convertToRaw, convertFromRaw} from 'draft-js';
import * as RB from 'react-bootstrap';
import Sticky from 'react-stickynode';
import jsonpatch from 'fast-json-patch';

import Navbar from './Navbar';
import ButtonToolbar from './ButtonToolbar';
import TextEditor from './TextEditor';
import Suggestions from './Suggestions';
import Utils from './Utils';
import EditorUtils from './EditorUtils';


function timestamp() {
  return Date.now() / 1000;
}


// edit: json
// timestamp: %Y-%m-%d %H:%M:%S.%f
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


// text: json
// timestamp: same
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


// generation_id: str
// draft_entity_id: str
// timestamp: same
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


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {init: false};

    // toolbar functions
    this.onTemperatureChange = (value) => this.setState({temperature: value});
    this.onSeqLenChange = (value) => this.setState({maxSeqLen: value});
    // editor functions
    this.insertHypAtCursor = this.insertHypAtCursor.bind(this);
    this.onEditorChange = this.onEditorChange.bind(this);
    this.handleKeyCommand = (command) => this._handleKeyCommand(command);
    this.onTab = (e) => this._onTab(e);
    this.toggleInlineStyle = (style) => this._toggleInlineStyle(style);
    this.handleBeforeInput = (char) => this._handleBeforeInput(char);
    // generation functions
    this.launchGeneration = this.launchGeneration.bind(this);
    this.onGenerate = this.onGenerate.bind(this);
    this.onRegenerate = this.onRegenerate.bind(this);
    // saving functions
    this.onInit = this.onInit.bind(this);
    this.saveInterval = this.saveInterval.bind(this);
  }

  onInit(session) {
    this.setState({
      // app state
      init: true,
      models: session.models,
      // editor state
      editorState: session.contentState ?
	EditorState.createWithContent(
	  convertFromRaw(session.contentState), EditorUtils.hypDecorator) :
	EditorState.createEmpty(EditorUtils.hypDecorator),
      lastEditorState: null,	// check if there were changes
      // generation variables
      temperature: session.temperature,
      maxSeqLen: session.maxSeqLen,
      batchSize: session.batchSize,
      hyps: [],
      lastSeed: null,	     // keep track of last seed for refreshing
      lastModel: null,	     // keep track of last model for refreshing
      // loading flags
      loadingHyps: false
    });
    // set interval
    this.saveIntervalId = setInterval(this.saveInterval, 25000);
  }

  saveInterval() {
    if (this.state.editorState !== this.state.lastEditorState) {
      saveDoc(convertToRaw(this.state.editorState.getCurrentContent()));
      this.setState({lastEditorState: this.state.editorState});
    }
  }

  componentDidMount() {
    init(this.onInit, (error) => console.log("Error"));
  }

  // editor functions
  _handleKeyCommand(command) {
    const {editorState} = this.state;
    const newState = RichUtils.handleKeyCommand(editorState, command);
    if (newState) {
      this.onEditorChange(newState);
      return true;
    }
    return false;
  }

  _onTab(e) {
    const maxDepth = 4;
    this.onEditorChange(RichUtils.onTab(e, this.state.editorState, maxDepth));
  }

  _toggleInlineStyle(inlineStyle) {
    this.onEditorChange(
      RichUtils.toggleInlineStyle(
        this.state.editorState,
        inlineStyle
      )
    );
  }

  _handleBeforeInput(char) {
    const {editorState} = this.state;
    const newState = EditorUtils.handleContiguousEntity(char, editorState);
    if (newState) {
      this.setState({editorState: newState});
      return true;
    }
    return false;
  }

  insertHypAtCursor(hyp) {
    const {eos, bos, par, text, score, generation_id} = hyp;
    const {editorState} = this.state;
    const contentStateWithHyp = EditorUtils.insertGeneratedText(
      editorState, text, {score: score, source: text, model: this.state.lastModel});
    const draftEntityId = contentStateWithHyp.getLastCreatedEntityKey();
    const newEditorState = EditorState.push(
      editorState, contentStateWithHyp, 'insert-characters');
    this.onEditorChange(newEditorState);
    saveSuggestion(generation_id, draftEntityId);
  }
  
  onEditorChange(editorState) {
    const oldState = this.state.editorState;
    const oldContent = oldState.getCurrentContent();
    const newContent = editorState.getCurrentContent();
    if (oldContent !== newContent) {
      // handle new metadata
      EditorUtils.updateHypMetadata(editorState);
      // block-level diff
      const selection = editorState.getSelection();
      const currentBlock = EditorUtils.getSelectedBlocks(newContent, selection);
      const oldBlock = EditorUtils.getSelectedBlocks(oldContent, selection);
      saveChange(jsonpatch.compare(oldBlock.toJS(), currentBlock.toJS()));
    }
    this.setState({editorState});
  }

  // generation functions
  launchGeneration(seed, model) {
    console.log(`Generating with seed: [${seed}]`);
    const {temperature, maxSeqLen} = this.state;
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: 'generate',
      data: JSON.stringify(
	{'selection': seed,
	 'temperature': temperature,
	 'model_path': model.path,
	 'max_seq_len': maxSeqLen}),
      type: 'POST',
      dataType: 'json',
      success: (response) => {
	this.setState(
	  {hyps: response.hyps,
	   lastSeed: seed,
	   lastModel: model,
	   loadingHyps: false}); // todo, update model status if it was loaded
      },
      error: (error) => {
	console.log(error);
	this.setState({loadingHyps: false});
      }
    });
    this.setState({loadingHyps: true});
  }

  onGenerate(model) {
    const {editorState} = this.state;
    const currentContent = editorState.getCurrentContent();
    const selection = editorState.getSelection();
    let seed = EditorUtils.getTextSelection(currentContent, selection);
    if (seed.trim().length == 0) {
      seed = currentContent.getPlainText('\n');
      if (seed.length > 200) seed = seed.substring(seed.length - 200);
    }
    this.launchGeneration(seed, model);
  }

  onRegenerate() {
    this.launchGeneration(this.state.lastSeed, this.state.lastModel);
  }

  render() {
    if (!this.state.init) {
      return (
	<RB.Grid>
	  <RB.Row>
	    <RB.Col md={2}/>
	    <RB.Col md={8}>
	      <RB.Jumbotron style={{backgroundColor:"#f5f5f5"}}>
		      <h2>Loading...</h2>
	      </RB.Jumbotron>
	    </RB.Col>
	    <RB.Col md={2}/>
	  </RB.Row>
	</RB.Grid>
      );
    } else {
      return (
	<div>
	  <Navbar/>
	  <RB.Grid fluid={true}>
	    <RB.Row>
	      <RB.Col md={3} sm={1}></RB.Col>
	      <RB.Col md={6} sm={10}>

		<RB.Row>
		  <Sticky enabled={true} top={0} innerZ={1001}>
		    <div className="panel panel-default generate-panel">
		      <div className="panel-heading">
			<ButtonToolbar
			   temperature={this.state.temperature} 
			   onTemperatureChange={this.onTemperatureChange}
			   maxSeqLen={this.state.maxSeqLen}
			   onSeqLenChange={this.onSeqLenChange}
			   models={this.state.models}
			   onGenerate={this.onGenerate}/>
		      </div>
		    </div>
		  </Sticky>
		</RB.Row>

		<RB.Row>
		  <TextEditor
		     editorState={this.state.editorState}
		     onChange={this.onEditorChange}
		     handleKeyCommand={this.handleKeyCommand}
		     onTab={this.onTab}
		     toggleInlineStyle={this.toggleInlineStyle}
		     handleBeforeInput={this.handleBeforeInput}/>
		</RB.Row>

		<RB.Row>
    		  <Utils.Spacer height="25px"/>
    		  <Suggestions
    		     hyps={this.state.hyps}
    		     loadingHyps={this.state.loadingHyps}
    		     onRegenerate={this.onRegenerate}
    		     onHypSelect={this.insertHypAtCursor}/>
		</RB.Row>
		
	      </RB.Col>
	      <RB.Col md={3} sm={1}></RB.Col>
	    </RB.Row>

	  </RB.Grid>
	</div>
      );
    }
  }
};


ReactDOM.render(<App/>, document.getElementById('app'));

