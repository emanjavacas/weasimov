import React from 'react';
import ReactDOM from 'react-dom';
import {Editor, EditorState, RichUtils} from 'draft-js';
import * as RB from 'react-bootstrap';
import Sticky from 'react-stickynode';

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
      <Sticky enabled={true} top={70} innerZ={1001}>
        <InlineStyleControls
           editorState={editorState}
           onToggle={this.props.toggleInlineStyle}
           />
      </Sticky>
        <div className={className} onClick={this.focus}>
          <Editor
            editorState={editorState}
            handleKeyCommand={this.props.handleKeyCommand}
            onChange={this.props.onChange}
            onTab={this.props.onTab}
            placeholder="Bieb bieb..."
            ref="editor"
            spellCheck={false}
	    handleBeforeInput={this.props.handleBeforeInput}
	   />
        </div>
      </div>
    );
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
      <RB.Button bsSize="small" onMouseDown={this.onToggle}>
	<span className={className}>
	  { this.props.icon ? <i className={"fa fa-" + this.props.icon}/> : this.props.label }
	</span>
      </RB.Button>
    );
  }
}

const INLINE_STYLES = [
  {label: 'Bold', style: 'BOLD', icon: 'bold'},
  {label: 'Italic', style: 'ITALIC', icon: 'italic'},
  {label: 'Underline', style: 'UNDERLINE', icon: 'underline'},
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
