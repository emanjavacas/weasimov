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


function insertGeneratedText(editorState, text, type, mutable, data) {
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
    if (startOffset > 0) {// we are not at the start of the block
      // TODO: add an if check for when being inside HYP entity
      // and if so update entity data as follows:
      // contentState.mergeEntityData(entityKey, {"edits": +1})
      const entityKeyBeforeCaret = block.getEntityAt(startOffset - 1);
      const entityKeyAfterCaret = block.getEntityAt(startOffset);
      const isCaretOutsideEntity = (entityKeyBeforeCaret !== entityKeyAfterCaret);
      if (entityKeyBeforeCaret && isCaretOutsideEntity) {
        const entity = contentState.getEntity(entityKeyBeforeCaret);
        const isMutable = entity.getMutability() === "MUTABLE";
        const { contiguous = true } = entity.getData();
        // if entity is mutable and not contiguous, and caret is to its right
        // insert new char without entity styling
        if (isMutable && !contiguous) {
          contentState = Modifier.insertText(
            contentState,
            selection,
            char,
            editorState.getCurrentInlineStyle(),
            null
          );
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

const Hyp = (props) => {
  // TODO: make color dependent from number of edits
  const data = props.contentState.getEntity(props.entityKey).getData();
  return <span style={hypStyle}>{props.children}</span>;
};

const hypDecorator = new CompositeDecorator([{strategy: findHyps, component: Hyp}]);


const EditorUtils = {
  insertGeneratedText: insertGeneratedText,
  handleContiguousEntity: handleContiguousEntity,
  getTextSelection: getTextSelection,
  hypDecorator: hypDecorator
};

export default EditorUtils;
