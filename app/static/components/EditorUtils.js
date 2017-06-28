import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, Modifier, CompositeDecorator} from 'draft-js';

import Levenshtein from 'fast-levenshtein';


function getSelectedBlocks(contentState, selection) {
  const startKey = selection.getStartKey(), endKey = selection.getEndKey();
  return contentState.getBlockMap()
    .skipUntil((block) => block.getKey() === startKey).reverse()
    .skipUntil((block) => block.getKey() === endKey).reverse();
}


function getTextSelection(contentState, selection, blockDelimiter) {
  const startKey = selection.getStartKey(), endKey = selection.getEndKey();

  return getSelectedBlocks(contentState, selection)
    .map((block) => {
      const key = block.getKey();
      const text = block.getText();
      let start = 0, end = text.length;
      if (key === startKey) start = selection.getStartOffset();
      if (key === endKey) end = selection.getEndOffset();
      return text.slice(start, end);;
    }).join(blockDelimiter || '\n');
}


function findHyps(contentBlock, callback, contentState) {
  contentBlock.findEntityRanges((char) => {
    const entityKey = char.getEntity();
    return (entityKey !== null && contentState.getEntity(entityKey).getType() === 'HYP');
  }, callback);
};


function insertGeneratedText(editorState, text, data) {
  data['contiguous'] = false;	// HYP entities are not contiguous
  data['skips'] = 0;
  data['prevText'] = null;
  const selection = editorState.getSelection();
  const currentContent = editorState.getCurrentContent().createEntity('HYP', 'MUTABLE', data);
  const entityKey = currentContent.getLastCreatedEntityKey();
  return Modifier.insertText(currentContent, selection, text, null, entityKey);
}


function getEntityText(block, offset, entityKey) {
  let result = '', startOffset = offset, endOffset = offset;
  let startEntity = block.getEntityAt(offset);
  let endEntity = block.getEntityAt(offset);
  while (startEntity && startEntity === entityKey) {
    startEntity = block.getEntityAt(--startOffset);
  }
  while (endEntity === entityKey) {
    endEntity = block.getEntityAt(++endOffset);
  }
  return block.getText().slice(startOffset + 1, endOffset);
}


function getNormLev(s1, s2) {
  const lev = Levenshtein.get(s1, s2);
  // normalized levenshtein
  // - lower bound: different in size between strings
  // - upper bound: length of the longest string
  const max = Math.max(s1.length, s2.length);
  console.log('lev', lev, 'normlev', lev / max, 'max', max);
  return lev/ max;
}


function updateHypMetadata(editorState, totalSkips, triggerOnStringDiff) {
  totalSkips = totalSkips || 5;
  triggerOnStringDiff = triggerOnStringDiff || 5;
  const selection = editorState.getSelection();
  if (selection.isCollapsed()) {
    const startKey = selection.getStartKey();
    const startOffset = selection.getStartOffset();
    let currentContent = editorState.getCurrentContent();
    const block = currentContent.getBlockForKey(startKey);
    if (startOffset > 0) {     // we are not at the start of the block
      const entityKeyBeforeCaret = block.getEntityAt(startOffset - 1);
      const entityKeyAfterCaret = block.getEntityAt(startOffset);
      const isCaretOutsideEntity = (entityKeyBeforeCaret !== entityKeyAfterCaret);
      if (entityKeyBeforeCaret && !isCaretOutsideEntity) {
	const entity = currentContent.getEntity(entityKeyBeforeCaret);
	const {skips, source, prevText} = entity.getData();
	if (entity.type === 'HYP') {
	  const entityText = getEntityText(block, startOffset, entityKeyBeforeCaret);
	  const prevTextLength = prevText ? prevText.length : entityText.length;
	  const diff = Math.abs(prevTextLength - entityText.length);
	  // only compute lev after 5 edits or an edit of length 5
	  if (skips >= totalSkips || diff > triggerOnStringDiff) {
	    currentContent.mergeEntityData(
	      entityKeyBeforeCaret,
	      {'lev': getNormLev(entityText, source),
	       'skips': 0,
	       'prevText': entityText});
	  } else {		// increase counters and previous text
	    currentContent.mergeEntityData(
	      entityKeyBeforeCaret, {'skips': skips + 1, 'prevText': entityText});
	  }
	}
      }
    }
  }
  return false;
}


function handleContiguousEntity(char, editorState) {
  const selection = editorState.getSelection();
  const startKey = selection.getStartKey();
  let currentContent = editorState.getCurrentContent();
  const block = currentContent.getBlockForKey(startKey);
  // handle the extending of mutable entities
  if (selection.isCollapsed()) { // no selection
    const startOffset = selection.getStartOffset();
    if (startOffset > 0) {     // we are not at the start of the block
      const entityKeyBeforeCaret = block.getEntityAt(startOffset - 1);
      const entityKeyAfterCaret = block.getEntityAt(startOffset);
      const isCaretOutsideEntity = (entityKeyBeforeCaret !== entityKeyAfterCaret);
      if (entityKeyBeforeCaret && isCaretOutsideEntity) {
	// handle border entity events
        const entity = currentContent.getEntity(entityKeyBeforeCaret);
        const isMutable = entity.getMutability() === "MUTABLE";
        const { contiguous = true } = entity.getData();
        if (isMutable && !contiguous) {
          currentContent = Modifier.insertText(
            currentContent, selection, char, editorState.getCurrentInlineStyle(), null);
	  return EditorState.push(editorState, currentContent, "insert-characters");
        }
      }
    }
  }
  return false;
}


function generalSigmoid(a, b, c) {
  a = a || 1, b = b || 1, c = c || 1;
  return function(x) {
    return a / (1 + b * Math.exp(-x * c));
  };
}


function getStyle(data) {
  let alpha = 1;
  const {r, g, b} = data.model.color;
  // const a = 1, b = 1000, inflection = 0.15;
  // const c = Math.log(b) / inflection;
  if (data.lev) {
    // alpha = 1 - generalSigmoid(a, b, c)(data.lev);
    alpha = 1 - data.lev;
  }
  return {'background': `rgba(${r},${g},${b},${alpha})`};
}


const Hyp = (props) => {
  const data = props.contentState.getEntity(props.entityKey).getData();
  return <span style={getStyle(data)}>{props.children}</span>;
};


const hypDecorator = new CompositeDecorator([{strategy: findHyps, component: Hyp}]);


const EditorUtils = {
  insertGeneratedText: insertGeneratedText,
  handleContiguousEntity: handleContiguousEntity,
  getTextSelection: getTextSelection,
  hypDecorator: hypDecorator,
  updateHypMetadata: updateHypMetadata,
  getSelectedBlocks: getSelectedBlocks
};

export default EditorUtils;
