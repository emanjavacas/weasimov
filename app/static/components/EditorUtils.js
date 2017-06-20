import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, Modifier, CompositeDecorator} from 'draft-js';


function getTextSelection(contentState, selection) {
  const blockDelimiter = '\n';
  const startKey = selection.getStartKey();
  const endKey = selection.getEndKey();
  const blocks = contentState.getBlockMap();

  const selectedBlock = blocks
	  .skipUntil((block) => block.getKey() === startKey).reverse()
	  .skipUntil((block) => block.getKey() === endKey).reverse();

  return selectedBlock.map((block) => {
    const key = block.getKey();
    const text = block.getText();
    let start = 0, end = text.length;
    if (key === startKey) {
      start = selection.getStartOffset();
    }
    if (key === endKey) {
      end = selection.getEndOffset();
    }
    return text.slice(start, end);;
  }).join(blockDelimiter);
}


function findHyps(contentBlock, callback, contentState) {
  contentBlock.findEntityRanges((char) => {
    const entityKey = char.getEntity();
    return (entityKey !== null && contentState.getEntity(entityKey).getType() === 'HYP');
  }, callback);
};


function insertText(editorState, text, type, mutable, data) {
  const selection = editorState.getSelection();
  const currentContent = editorState.getCurrentContent().createEntity(type, mutable, data);
  const entityKey = currentContent.getLastCreatedEntityKey();
  return Modifier.insertText(currentContent, selection, text, null, entityKey);
}


function handleContiguousEntity(char, editorState) {
  const selection = editorState.getSelection();
  let contentState = editorState.getCurrentContent();
  const startKey = selection.getStartKey();
  const block = contentState.getBlockForKey(startKey);
  // handle the extending of mutable entities
  if (selection.isCollapsed()) {
    const startOffset = selection.getStartOffset();
    if (startOffset > 0) {
      // we are not at the start of the block
      const entityKeyBeforeCaret = block.getEntityAt(startOffset - 1);
      const entityKeyAfterCaret = block.getEntityAt(startOffset);
      const isCaretOutsideEntity = (entityKeyBeforeCaret !== entityKeyAfterCaret);
      if (entityKeyBeforeCaret && isCaretOutsideEntity) {
        const entity = contentState.getEntity(entityKeyBeforeCaret);
        const isMutable = entity.getMutability() === "MUTABLE";
        const { contiguous = true } = entity.getData();
        // if entity is mutable, and caret is outside, and contiguous is set the false
        // remove the entity from the current char
        if (isMutable && !contiguous) {
          // insert the text into the contentState
          contentState = Modifier.insertText(
            contentState,
            selection,
            char,
            editorState.getCurrentInlineStyle(),
            null
          );
          // push the new content into the editor state
          const newEditorState = EditorState.push(
            editorState,
            contentState,
            "insert-characters"
          );
          return newEditorState;
        }
      }
    }
  }
  return false;
}


const hypStyle = {background: 'lightBlue'};

const Hyp = (props) => <span style={hypStyle}>{props.children}</span>;

const hypDecorator = new CompositeDecorator([{strategy: findHyps, component: Hyp}]);


const EditorUtils = {
  insertText: insertText,
  handleContiguousEntity: handleContiguousEntity,
  getTextSelection: getTextSelection,
  hypDecorator: hypDecorator
};

export default EditorUtils;
