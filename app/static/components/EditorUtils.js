import React from 'react';
import ReactDOM from 'react-dom';
import {EditorState, RichUtils, Modifier, CompositeDecorator} from 'draft-js';


function getTextSelection(contentState, selection) {
  const blockDelimiter = '\n';
  const startKey = selection.getStartKey();
  const endKey = selection.getEndKey();

  return contentState.getBlockMap()
    .skipUntil((block) => block.getKey() === startKey).reverse()
    .skipUntil((block) => block.getKey() === endKey).reverse()
    .map((block) => {
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


function insertGeneratedText(editorState, text, data) {
  data['contiguous'] = false;	// HYP entities are not contiguouos
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

function LCS(x,y){
  var s, i, j, m, n,
      lcs = [], row = [], c = [],
      left, diag, latch;
  //make sure shorter string is the column string
  if (m<n) {s=x; x=y; y=s;}
  m = x.length;
  n = y.length;
  //build the c-table
  for (j=0; j<n; row[j++]=0);
  for (i=0; i<m; i++) {
    c[i] = row = row.slice();
    for (diag=0, j=0; j<n;j++, diag=latch) {
      latch = row[j];
      if (x[i] == y[j]) {row[j] = diag+1;}
      else{
	left = row[j-1]||0;
	if (left>row[j]) {row[j] = left;}
      }
    }
  }
  i--,j--;
  //row[j] now contains the length of the lcs
  //recover the lcs from the table
  while (i>-1&&j>-1) {
    switch (c[i][j]) {
      default: j--;
      lcs.unshift(x[i]);
    case (i&&c[i-1][j]): i--;
      continue;
    case (j&&c[i][j-1]): j--;
    }
  }
  return lcs.join('');
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
      } else if (entityKeyBeforeCaret && !isCaretOutsideEntity) {
	// handle inside entity events
	const entity = currentContent.getEntity(entityKeyBeforeCaret);
	if (entity.type === 'HYP') {
	  const entityText = getEntityText(block, startOffset, entityKeyBeforeCaret);
	  currentContent = currentContent.mergeEntityData(
	    entityKeyBeforeCaret,
	    {'LCS': LCS(entity.getData().source, entityText)}); // todo get entity text from content block
	  console.log(LCS(entity.getData().source, entityText));
	  console.log(entity.getData().source, entityText);
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
