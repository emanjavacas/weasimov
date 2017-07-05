import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, convertToRaw, convertFromRaw, SelectionState} from 'draft-js';
import * as RB from 'react-bootstrap';
import Sticky from 'react-stickynode';
import NotificationSystem from 'react-notification-system';
import jsonpatch from 'fast-json-patch';

import Navbar from './Navbar';
import ButtonToolbar from './ButtonToolbar';
import TextEditor from './TextEditor';
import Suggestions from './Suggestions';
import Utils from './Utils';
import EditorUtils from './EditorUtils';


class App extends React.Component {

  constructor(props) {
    super(props);
    this.state = {init: false};
    // notification system
    this._notificationSystem = null;
    // toolbar functions
    this.onTemperatureChange = (value) => this.setState({temperature: value});
    this.onSeqLenChange = (value) => this.setState({maxSeqLen: value});
    // docs
    this.loadDoc = this.loadDoc.bind(this);
    this.onLoadDocSuccess = this.onLoadDocSuccess.bind(this);
    this.onLoadDocError = this.onLoadDocError.bind(this);
    this.createDoc = this.createDoc.bind(this);
    this.onCreateDocSuccess = this.onCreateDocSuccess.bind(this);
    this.onCreateDocError = this.onCreateDocError.bind(this);
    this.editDocName = this.editDocName.bind(this);
    this.updateNewScreenName = this.updateNewScreenName.bind(this);
    this.selectDoc = this.selectDoc.bind(this);
    this.getDocState = this.getDocState.bind(this);
    this.setDocState = this.setDocState.bind(this);
    // editor functions
    this.insertHypAtCursor = this.insertHypAtCursor.bind(this);
    this.onEditorChange = this.onEditorChange.bind(this);
    // suggestions
    this.dismissHyp = this.dismissHyp.bind(this);
    this.resetHyps = () => this.setState({hyps: []});
    this.toggleSuggestions = this.toggleSuggestions.bind(this);
    // editor
    this.handleKeyCommand = (command) => this._handleKeyCommand(command);
    this.onTab = (e) => this._onTab(e);
    this.toggleInlineStyle = (style) => this._toggleInlineStyle(style);
    this.handleBeforeInput = (char) => this._handleBeforeInput(char);
    // generation functions
    this.launchGeneration = this.launchGeneration.bind(this);
    this.onGenerationSuccess = this.onGenerationSuccess.bind(this);
    this.onGenerationError = this.onGenerationError.bind(this);
    this.generate = this.generate.bind(this);
    this.regenerate = this.regenerate.bind(this);
    // saving functions
    this.onInit = this.onInit.bind(this);
    this.saveOnInterval = this.saveOnInterval.bind(this);
    this.saveOnUnload = this.saveOnUnload.bind(this);
  }

  componentDidMount() {
    // init session
    Utils.init(this.onInit, (error) => console.log("Error"));
    // add unload event
    window.addEventListener("beforeunload", this.saveOnUnload);
  }

  componentWillUnmount() {
    window.removeEventListener("beforeunload", this.saveOnUnload);
  }

  // server interaction
  onInit(session) {
    this.setState({
      // app state
      init: true,
      username: session.username,
      models: session.models,
      docs: Utils.normalizeDocs(session.docs),
      docId: session.docId,
      // editor state
      editorStates: Utils.normalizeEditorState(
	session.docId,		// current docId
	session.docs.map((doc) => doc.id), // all docIds
	session.contentState ?		   // current doc editorState
	  EditorState.createWithContent(
	    convertFromRaw(session.contentState), EditorUtils.hypDecorator) :
	  EditorState.createEmpty(EditorUtils.hypDecorator)),
      lastEditorState: null,	// check if there were changes
      // generation variables
      temperature: session.temperature,
      maxSeqLen: session.maxSeqLen,
      hyps: [],
      lastSeed: null,	     // keep track of last seed for refreshing
      lastModel: null,	     // keep track of last model for refreshing
      // component flags
      loadingHyps: false,
      suggestionsCollapsed: true,
      hasHadHyps: false
    });
    // set interval
    this.saveOnIntervalId = setInterval(this.saveOnInterval, 25000);
  }

  setDocState(field, data) { // TODO: move active editorState to currentEditorState for performance
    this.setState({
      editorStates: {
	...this.state.editorStates,
	[this.state.docId]: {
	  ...this.state.editorStates[this.state.docId],
	  [field]: data
	}
      }
    });
  }

  saveOnInterval() {
    const {editorState, lastEditorState} = this.getDocState();
    if (!lastEditorState || editorState.getCurrentContent() !== lastEditorState.getCurrentContent()) {
      const text = convertToRaw(editorState.getCurrentContent());
      Utils.saveDoc(text, this.state.docId);
      this.setDocState('lastEditorState', editorState);
    }
  }

  saveOnUnload() {
    const {temperature, maxSeqLen} = this.state;
    Utils.saveSession({temperature, maxSeqLen});
    const {editorState, docId} = this.getDocState();
    Utils.saveDoc(convertToRaw(editorState.getCurrentContent()), docId);
  }

  // doc
  loadDoc(docId) {
    Utils.fetchDoc(docId, this.onLoadDocSuccess, this.onLoadDocError);
    this.setDocState('loading', true);
  }

  onLoadDocSuccess(response) {
    const editorState = response.contentState ?
	    EditorState.createWithContent() :
	    EditorState.createEmpty(EditorUtils.hypDecorator);
    this.setDocState('editorState', editorState);
    this.setDocState('loading', false);
    this.setState({docId});
  }

  onLoadDocError(error) {
    console.log("Couldn't load document");
  }

  createDoc(screenName) {
    Utils.createDoc(screenName, this.onCreateDocSuccess, this.onCreateDocError);
  }

  onCreateDocSuccess(response) {
    const {editorStates, docs} = this.state;
    docs[response.doc.id] = response.doc;
    editorStates[response.doc.id] = Utils.newDocState(
      response.doc.id,
      EditorState.createEmpty(EditorUtils.hypDecorator)
    );
    this.setState({editorStates: editorStates, docs: docs});
  }

  onCreateDocError(response) {
    console.log("Couldn't create document.");
  }

  updateNewScreenName(docId, newName) {
    const doc = this.state.docs[docId];
    doc['screen_name'] = newName;
    this.setState({docs: {...this.state.docs, [docId]: doc}});
  }

  editDocName(newName) {
    Utils.editDocName(
      this.state.docId,
      newName,
      () => this.updateNewScreenName(this.state.docId, newName),
      () => console.log("Couldn't update document name")
    );
  }

  onNewDoc() {
    
  }

  selectDoc(docId) {
    if (docId != this.state.docId) {
      this.saveOnInterval(); this.setState({docId});
    }
  }

  getDocState() {
    return this.state.editorStates[this.state.docId];
  }

  // generation functions
  onGenerationSuccess(response) {
    // append seed for convenience
    const incomingHyps = response.hyps.map((hyp) => Object.assign(hyp, {'seed': response.seed}));
    this.setState(
      {hyps: incomingHyps.concat(this.state.hyps),
       lastSeed: response.seed,
       lastModel: response.model,
       loadingHyps: false,
       hasHadHyps: true});
    this.toggleSuggestions(false);
  }

  onGenerationError(error) {
    console.log(error);
    this.setState({loadingHyps: false});
  }
  
  launchGeneration(seed, model) {
    console.log(`Generating with seed: [${seed}]`);
    const {temperature, maxSeqLen, docId} = this.state;
    Utils.launchGeneration(
      seed,
      model,
      {temperature, maxSeqLen, docId},
      this.onGenerationSuccess,
      this.onGenerationError);
    this.setState({loadingHyps: true});
  }

  generate(model) {
    const {editorState} = this.getDocState();
    const currentContent = editorState.getCurrentContent();
    const selection = editorState.getSelection();
    let seed = EditorUtils.getTextSelection(currentContent, selection);
    if (seed.trim().length == 0) {
      seed = currentContent.getPlainText('\n');
      if (seed.length > 200) seed = seed.substring(seed.length - 200);
    }
    this.launchGeneration(seed, model);
  }

  regenerate() {
    this.launchGeneration(this.state.lastSeed, this.state.lastModel);
  }

  // editor functions
  insertHypAtCursor(hyp) {
    // insert the hyp
    const {editorState} = this.getDocState();
    const {models} = this.state;
    let selection = editorState.getSelection();
    if (!selection.isCollapsed()) { // collapse selection if not already so
      selection = new SelectionState(
	{anchorKey: selection.getAnchorKey(),
	 anchorOffset: selection.getEndOffset(),
	 focusKey: selection.getAnchorKey(),
	 focusOffset: selection.getEndOffset()}
      );
    }
    const {eos, bos, par, text, score, generation_id, model} = hyp;
    const modelData = Utils.getModelData(models, model);
    const contentStateWithHyp = EditorUtils.insertGeneratedText(
      editorState, text, {score: score, source: text, model: modelData}, selection);
    const newEditorState = EditorState.push(
      editorState, contentStateWithHyp, 'insert-characters');
    this.onEditorChange(newEditorState);
    // send selection to server
    const draftEntityId = contentStateWithHyp.getLastCreatedEntityKey();
    const docId = this.state.docId;
    Utils.saveSuggestion(generation_id, docId, 'selected', draftEntityId);
  }
  
  onEditorChange(newEditorState) {
    const {editorState} = this.getDocState();
    const oldContent = editorState.getCurrentContent();
    const newContent = newEditorState.getCurrentContent();
    if (oldContent !== newContent) {
      // handle new metadata
      EditorUtils.updateHypMetadata(newEditorState);
      // block-level diff
      const selection = newEditorState.getSelection();
      const currentBlock = EditorUtils.getSelectedBlocks(newContent, selection);
      const oldBlock = EditorUtils.getSelectedBlocks(oldContent, selection);
      const edit = jsonpatch.compare(oldBlock.toJS(), currentBlock.toJS());
      Utils.saveChange(edit, this.state.docId);
    }
    this.setDocState('editorState', newEditorState);
  }

  dismissHyp(hypId) {
    let dismissedHyp, newHyps = [];
    for (var i=0; i<this.state.hyps.length; i++) {
      const hyp = this.state.hyps[i];
      if (hyp.generation_id === hypId) {
	dismissedHyp = this.state.hyps[i];
      } else {
	newHyps.push(hyp);
      }
    }
    this.setState({hyps: newHyps});
    Utils.saveSuggestion(hypId, this.state.docId, 'dismissed');
  }

  toggleSuggestions(newState) {
    if (newState !== undefined) {
      this.setState({suggestionsCollapsed: newState});
    } else {
      this.setState({suggestionsCollapsed: !this.state.suggestionsCollapsed});
    }
  }
 
  _handleKeyCommand(command) {
    const {editorState} = this.getDocState();
    const newState = RichUtils.handleKeyCommand(editorState, command);
    if (newState) {
      this.onEditorChange(newState);
      return true;
    }
    return false;
  }

  _onTab(e) {
    const maxDepth = 4;
    const {editorState} = this.getDocState();
    this.onEditorChange(RichUtils.onTab(e, editorState, maxDepth));
  }

  _toggleInlineStyle(inlineStyle) {
    const {editorState} = this.getDocState();
    this.onEditorChange(RichUtils.toggleInlineStyle(editorState, inlineStyle));
  }

  _handleBeforeInput(char) {
    const {editorState} = this.getDocState();
    const newState = EditorUtils.handleContiguousEntity(char, editorState);
    if (newState) {
      this.onEditorChange(newState);
      return true;
    }
    return false;
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
	  <Navbar
	     username={this.state.username}
	     activeDoc={this.state.docId}
	     docs={this.state.docs}
	     onSelectDoc={this.selectDoc}
	     onSubmitScreenName={this.editDocName}/>
	  <NotificationSystem ref={(el) => {this._notificationSystem = el;}}/>
	  <RB.Grid fluid={true}>
	    <RB.Row>
	      <RB.Col lg={2} md={2} sm={1}></RB.Col>
	      <RB.Col lg={8} md={8} sm={10}>

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
			   onGenerate={this.generate}/>
		      </div>
		    </div>
		  </Sticky>
		</RB.Row>

		<RB.Row>
		  <TextEditor
		     editorState={this.getDocState().editorState}
		     onChange={this.onEditorChange}
		     handleKeyCommand={this.handleKeyCommand}
		     onTab={this.onTab}
		     toggleInlineStyle={this.toggleInlineStyle}
		     handleBeforeInput={this.handleBeforeInput}/>
		  <Utils.Spacer height="50px"/>
		</RB.Row>

		<RB.Row>
    		  <Suggestions
    		     hyps={this.state.hyps}
		     models={this.state.models}
		     isCollapsed={this.state.suggestionsCollapsed}
		     onCollapse={this.toggleSuggestions}
    		     loadingHyps={this.state.loadingHyps}
    		     onRegenerate={this.regenerate}
    		     onHypSelect={this.insertHypAtCursor}
		     onHypDismiss={this.dismissHyp}
		     hasHadHyps={this.state.hasHadHyps}
		     resetHyps={this.resetHyps}/>
		</RB.Row>
		
	      </RB.Col>
	      <RB.Col lg={2} md={2} sm={1}></RB.Col>
	    </RB.Row>

	  </RB.Grid>
	</div>
      );
    }
  }
};


ReactDOM.render(<App/>, document.getElementById('app'));

