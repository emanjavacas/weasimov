import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, Modifier, CompositeDecorator} from 'draft-js';

import ButtonToolbar from './ButtonToolbar';
import TextEditor from './TextEditor';
import Suggestions from './Suggestions';
import Utils from './Utils';
import EditorUtils from './EditorUtils';


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      temperature: 0.35,
      maxSeqLen: 200,
      currentModel: null,
      hyps: [],
      lastSeed: null,
      loadingHyps: false,
      editorState: EditorState.createEmpty(EditorUtils.hypDecorator)
    };

    // toolbar functions
    this.onSliderChange = (value) => this.setState({temperature: value});
    this.onModelSelect = (model) => this.setState({currentModel: model});
    this.onSeqLenChange = (value) => this.setState({maxSeqLen: value});
    // editor functions
    this.insertHypAtCursor = this.insertHypAtCursor.bind(this);
    this.onEditorChange = this.onEditorChange.bind(this);
    this.handleKeyCommand = (command) => this._handleKeyCommand(command);
    this.onTab = (e) => this._onTab(e);
    this.toggleBlockType = (type) => this._toggleBlockType(type);
    this.toggleInlineStyle = (style) => this._toggleInlineStyle(style);
    this.handleBeforeInput = (char) => this._handleBeforeInput(char);
    // generation functions
    this.launchGeneration = this.launchGeneration.bind(this);
    this.onGenerate = this.onGenerate.bind(this);
    this.onRegenerate = this.onRegenerate.bind(this);
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

  _toggleBlockType(blockType) {
    this.onEditorChange(
      RichUtils.toggleBlockType(
        this.state.editorState,
        blockType
      )
    );
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
    const {eos, bos, par, text, score} = hyp;
    const {editorState} = this.state;
    const stateWithHyp = EditorUtils.insertText(
      editorState,
      text,
      'HYP', 'MUTABLE', {score: score, contiguous: false});
    this.setState({
      editorState: EditorState.push(editorState, stateWithHyp, 'insert-characters')
    });
  }
  
  onEditorChange(editorState) {
    this.setState({editorState});
  }

  // generation functions
  launchGeneration(seed) {
    console.log("Generating with seed: ", seed);
    const {temperature, currentModel, maxSeqLen} = this.state;
    if (!currentModel) {
      alert('Pick a model first!');
      return;
    }
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: 'generate',
      data: JSON.stringify(
    	{'selection': seed,
    	 'temperature': temperature,
    	 'model_name': currentModel,
	 'max_seq_len': maxSeqLen}),
      type: 'POST',
      dataType: 'json',
      success: (response) => {
    	this.setState({hyps: response.hyps, lastSeed: seed, loadingHyps: false});
      },
      error: (error) => {
    	console.log(error);
	this.setState({loadingHyps: false});
      }
    });
    this.setState({loadingHyps: true});
  }

  onGenerate() {
    const {editorState} = this.state;
    const currentContent = editorState.getCurrentContent();
    const selection = editorState.getSelection();
    let seed = EditorUtils.getTextSelection(currentContent, selection);
    if (seed.trim().length == 0) { seed = currentContent.getPlainText('\n'); }
    this.launchGeneration(seed);
  }

  onRegenerate() {
    this.launchGeneration(this.state.lastSeed);
  }

  render() {
    return (
      <div className="container-fluid">
	<div className="row">
          <div className="col-md-2"></div>
          <div className="col-md-8">
	    <div className="row"><h1>Ik, Asimov</h1></div>
            <Utils.Spacer height="45px"/>
            <div className="row">
	      <ButtonToolbar
		 onGenerate={this.onGenerate}
		 onSliderChange={this.onSliderChange}
		 onModelSelect={this.onModelSelect}
		 temperature={this.state.temperature}
		 currentModel={this.state.currentModel}
		 maxSeqLen={this.state.maxSeqLen}
		 onSeqLenChange={this.onSeqLenChange}
		 sizes={[10, 20, 30, 50, 75, 100, 150, 200, 250, 300]}/>
	    </div>
	    <Utils.Spacer height="25px"/>
	    <div className="row">
	      <TextEditor
		 editorState={this.state.editorState}
		 onChange={this.onEditorChange}
		 handleKeyCommand={this.handleKeyCommand}
		 onTab={this.onTab}
		 toggleBlockType={this.toggleBlockType}
		 toggleInlineStyle={this.toggleInlineStyle}
		 handleBeforeInput={this.handleBeforeInput}/>
	    </div>
	    <Utils.Spacer height="25px"/>
	    <div className="row">
	      <Suggestions
		 hyps={this.state.hyps}
		 loadingHyps={this.state.loadingHyps}
		 onRegenerate={this.onRegenerate}
		 onHypSelect={this.insertHypAtCursor}/>
	    </div>
	  </div>
	  <div className="col-md-2"></div>
	</div>
      </div>
    );
  }
};


ReactDOM.render(<App/>, document.getElementById('app'));
