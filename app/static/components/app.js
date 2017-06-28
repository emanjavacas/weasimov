import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, convertToRaw} from 'draft-js';
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


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      // generation variables
      temperature: 0.35,
      maxSeqLen: 200,
      batchSize: 5,
      currentModel: null,
      hyps: [],
      lastSeed: null,		// keep track of last seed for refreshing
      // loading flags
      loadingHyps: false,
      // editor state
      editorState: EditorState.createEmpty(EditorUtils.hypDecorator),
      lastEditorState: null	// don't save editor state if there were no changes
    };

    // toolbar functions
    this.onSliderChange = (value) => this.setState({temperature: value});
    this.onModelSelect = (model) => this.setState({currentModel: model});
    this.onSeqLenChange = (value) => this.setState({maxSeqLen: value});
    this.onBatchSizeChange = (value) => this.setState({batchSize: value});
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
    // saving functions
    this.saveInterval = this.saveInterval.bind(this);
  }

  componentDidMount() {
    this.saveIntervalId = setInterval(this.saveInterval, 25000);
  }

  saveInterval() {
    if (this.state.editorState !== this.state.lastEditorState) {
      saveDoc(this.state.editorState);
      this.setState({lastEditorState: this.state.editorState});
    }
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
    const {eos, bos, par, text, score, generation_id} = hyp;
    const {editorState} = this.state;
    const contentStateWithHyp = EditorUtils.insertGeneratedText(
      editorState, text, {score: score, source: text});
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
  launchGeneration(seed) {
    console.log(`Generating with seed: [${seed}]`);
    const {temperature, currentModel, maxSeqLen, batchSize} = this.state;
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
	 'max_seq_len': maxSeqLen,
	 'batch_size': batchSize}),
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
      <div>
	<Navbar/>
	<RB.Grid fluid={true}>
	<RB.Row>
	  <RB.Col md={3} sm={1}></RB.Col>
	  <RB.Col md={6} sm={10}>
          <Sticky enabled={true} top={0} innerZ={1001}>
            <div className="panel panel-default generate-panel">
              <div className="panel-heading">
                <ButtonToolbar
             onGenerate={this.onGenerate}
             onSliderChange={this.onSliderChange}
             onModelSelect={this.onModelSelect}
             temperature={this.state.temperature} 
             currentModel={this.state.currentModel}
             maxSeqLen={this.state.maxSeqLen}
             onSeqLenChange={this.onSeqLenChange}
             batchSize={this.state.batchSize}
             onBatchSizeChange={this.onBatchSizeChange}
             batchSizes={[1, 2, 3, 4, 5, 10, 15]}
             sizes={[10, 20, 30, 50, 75, 100, 150, 200, 250, 300]}/>
              </div>
            </div>
          </Sticky>
    </RB.Col>
    <RB.Col md={3} sm={1}></RB.Col>
  </RB.Row>

  <RB.Row>
    <RB.Col md={3} sm={1}></RB.Col>
    <RB.Col md={6} sm={10}>
      <TextEditor
         editorState={this.state.editorState}
         onChange={this.onEditorChange}
         handleKeyCommand={this.handleKeyCommand}
         onTab={this.onTab}
         toggleBlockType={this.toggleBlockType}
         toggleInlineStyle={this.toggleInlineStyle}
         handleBeforeInput={this.handleBeforeInput}/>
    </RB.Col>
    <RB.Col md={3} sm={1}></RB.Col>
  </RB.Row>
   
  <RB.Row>
    <RB.Col md={3} sm={1}></RB.Col>
      <RB.Col md={6}>
    		<Utils.Spacer height="25px"/>
    		<Suggestions
    		   hyps={this.state.hyps}
    		   loadingHyps={this.state.loadingHyps}
    		   onRegenerate={this.onRegenerate}
    		   onHypSelect={this.insertHypAtCursor}/>
      </RB.Col>

      <RB.Col md={3} sm={1}>
      </RB.Col>
  </RB.Row>
    
</RB.Grid>
      </div>
    );
  }
};


ReactDOM.render(<App/>, document.getElementById('app'));

