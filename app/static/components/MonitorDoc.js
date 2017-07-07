
import React from 'react';
import ReactDOM from 'react-dom';
import {Editor, EditorState, RichUtils} from 'draft-js';

class MonitorDoc extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      init: false
    };
  }

  componentDidMount() {
    this.props.onLoadDoc(this.props.activeRoom);
  }

  render() {
    return (
      <div className="RichEditor-root RichEditor-editor">
	<Editor
	   readOnly={true}
           editorState={this.props.editorState}
           onChange={this.props.onChange}
           ref="editor"/>
      </div>
    );
  }
}

export default MonitorDoc;
