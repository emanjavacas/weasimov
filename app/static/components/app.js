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
    // editor functions
    this.insertHypAtCursor = this.insertHypAtCursor.bind(this);
    this.onEditorChange = this.onEditorChange.bind(this);
    //suggestions
    this.dismissHyp = this.dismissHyp.bind(this);
    this.resetHyps = () => this.setState({hyps: []});
    this.toggleSuggestions = this.toggleSuggestions.bind(this);
    // Editor
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
    this.saveInterval = this.saveInterval.bind(this);
    this.saveUnload = this.saveUnload.bind(this);
  }

  componentDidMount() {
    // init session
    Utils.init(this.onInit, (error) => console.log("Error"));
    // add unload event
    window.addEventListener("beforeunload", this.saveUnload);
  }

  componentWillUnmount() {
    window.removeEventListener("beforeunload", this.saveUnload);
  }

  // server interaction
  onInit(session) {
    this.setState({
      // app state
      init: true,
      username: session.username,
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
      hyps: [],
      lastSeed: null,	     // keep track of last seed for refreshing
      lastModel: null,	     // keep track of last model for refreshing
      // component flags
      loadingHyps: false,
      suggestionsCollapsed: true,
      hasHadHyps: false
    });
    // set interval
    this.saveIntervalId = setInterval(this.saveInterval, 25000);
  }

  saveInterval() {
    if (this.state.editorState !== this.state.lastEditorState) {
      Utils.saveDoc(convertToRaw(this.state.editorState.getCurrentContent()));
      this.setState({lastEditorState: this.state.editorState});
    }
  }

  saveUnload() {
    Utils.saveSession(this.state);
    Utils.saveDoc(convertToRaw(this.state.editorState.getCurrentContent()));
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
    this.refs.suggestions.refs.suggestionlist.scrollUp();
  }

  onGenerationError(error) {
    console.log(error);
    this.setState({loadingHyps: false});
  }
  
  launchGeneration(seed, model) {
    console.log(`Generating with seed: [${seed}]`);
    Utils.launchGeneration(seed, model, this.state, this.onGenerationSuccess, this.onGenerationError);
    this.setState({loadingHyps: true});
  }

  generate(model) {
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

  regenerate() {
    this.launchGeneration(this.state.lastSeed, this.state.lastModel);
  }

  // editor functions
  insertHypAtCursor(hyp) {
    const {editorState, models} = this.state;
    let selection = editorState.getSelection();
    if (!selection.isCollapsed()) {
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
    const draftEntityId = contentStateWithHyp.getLastCreatedEntityKey();
    const newEditorState = EditorState.push(
      editorState, contentStateWithHyp, 'insert-characters');
    this.onEditorChange(newEditorState);
    Utils.saveSuggestion(generation_id, draftEntityId);
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
      Utils.saveChange(jsonpatch.compare(oldBlock.toJS(), currentBlock.toJS()));
    }
    this.setState({editorState});
  }

  dismissHyp(hypId) {
    this.setState({hyps: this.state.hyps.filter((hyp) => hyp.generation_id !== hypId)});
  }

  toggleSuggestions(newState) {
    if (newState !== undefined) {
      this.setState({suggestionsCollapsed: newState});
    } else {
      this.setState({suggestionsCollapsed: !this.state.suggestionsCollapsed});
    }
  }
 
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
	  <Navbar username={this.state.username}/>
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
		     editorState={this.state.editorState}
		     onChange={this.onEditorChange}
		     handleKeyCommand={this.handleKeyCommand}
		     onTab={this.onTab}
		     toggleInlineStyle={this.toggleInlineStyle}
		     handleBeforeInput={this.handleBeforeInput}/>
		  <Utils.Spacer height="50px"/>
		</RB.Row>

		<RB.Row>
    		  <Suggestions
             ref="suggestions"
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

