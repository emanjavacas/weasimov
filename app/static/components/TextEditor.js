import React from 'react';
import ReactDOM from 'react-dom';
import {Editor, EditorState, RichUtils} from 'draft-js';
import * as RB from 'react-bootstrap';


class TextEditor extends React.Component {
  constructor(props) {
    super(props);
    this.state = {};
    this.focus = () => this.refs.editor.focus();
  }

  render() {
    const {editorState} = this.props;

    // If the user changes block type before entering any text, we can
    // either style the placeholder or hide it. Let's just hide it now.
    let className = 'RichEditor-editor';
    var contentState = editorState.getCurrentContent();
    if (!contentState.hasText()) {
      if (contentState.getBlockMap().first().getType() !== 'unstyled') {
        className += ' RichEditor-hidePlaceholder';
      }
    }

    return (
      <div className="RichEditor-root">
        <BlockStyleControls
           editorState={editorState}
           onToggle={this.props.toggleBlockType}
           />
        <InlineStyleControls
           editorState={editorState}
           onToggle={this.props.toggleInlineStyle}
           />
        <div className={className} onClick={this.focus}>
          <Editor
             blockStyleFn={getBlockStyle}
             editorState={editorState}
             handleKeyCommand={this.props.handleKeyCommand}
             onChange={this.props.onChange}
             onTab={this.props.onTab}
             placeholder="Biep biep..."
             ref="editor"
             spellCheck={false}
	     handleBeforeInput={this.props.handleBeforeInput}
	     />
        </div>
      </div>
    );
  }
}

function getBlockStyle(block) {
  switch (block.getType()) {
  case 'blockquote': return 'RichEditor-blockquote';
  default: return null;
  }
}

class StyleButton extends React.Component {
  constructor() {
    super();
    this.onToggle = (e) => {
      e.preventDefault();
      this.props.onToggle(this.props.style);
    };
  }

  render() {
    let className = 'RichEditor-styleButton';
    if (this.props.active) {
      className += ' RichEditor-activeButton';
    }

    return (
      <RB.Button bsSize="xsmall">
	<span className={className} onMouseDown={this.onToggle}>
	  { this.props.icon ? <i className={"fa fa-" + this.props.icon}/> : this.props.label }
	</span>
      </RB.Button>
    );
  }
}

const BLOCK_TYPES = [
  {label: 'H1', style: 'header-one'},
  {label: 'H2', style: 'header-two'},
  {label: 'H3', style: 'header-three'},
  {label: 'H4', style: 'header-four'},
  {label: 'H5', style: 'header-five'},
  {label: 'Blockquote', style: 'blockquote', icon: 'quote-right'},
  {label: 'UL', style: 'unordered-list-item', icon: 'list-ul'},
  {label: 'OL', style: 'ordered-list-item', icon: 'list-ol'},
  {label: 'Code Block', style: 'code-block', icon: 'code'},
];

const BlockStyleControls = (props) => {
  const {editorState} = props;
  const selection = editorState.getSelection();
  const blockType = editorState
	  .getCurrentContent()
	  .getBlockForKey(selection.getStartKey())
	  .getType();

  return (
    <div className="RichEditor-controls">
      {BLOCK_TYPES.map((type) =>
		       <StyleButton
			    key={type.label}
			    active={type.style === blockType}
			    label={type.label}
			    onToggle={props.onToggle}
			    style={type.style}
			    icon={type.icon}
			    />
		      )}
    </div>
  );
};

var INLINE_STYLES = [
  {label: 'Bold', style: 'BOLD', icon: 'bold'},
  {label: 'Italic', style: 'ITALIC', icon: 'italic'},
  {label: 'Underline', style: 'UNDERLINE', icon: 'underline'},
  {label: 'Monospace', style: 'CODE', icon: 'font'},
];

const InlineStyleControls = (props) => {
  var currentStyle = props.editorState.getCurrentInlineStyle();
  return (
    <div className="RichEditor-controls">
      {INLINE_STYLES.map(type =>
			 <StyleButton
			      key={type.label}
			      active={currentStyle.has(type.style)}
			      label={type.label}
			      onToggle={props.onToggle}
			      style={type.style}
			      icon={type.icon}
			      />
			)}
    </div>
  );
};

export default TextEditor;
