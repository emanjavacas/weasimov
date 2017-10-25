
import React from 'react';
import ReactDOM from 'react-dom';
import * as RB from 'react-bootstrap';
import { CSSTransitionGroup } from 'react-transition-group';

import Utils from './Utils';


class HypItem extends React.Component {
  render() {
    const {hyp, backgroundColor, onHypSelect, onHypDismiss} = this.props;
    return (
				<div 
					onClick={() => onHypSelect(hyp)}
					className="suggestie"
					style={{color:backgroundColor}}>
					<span className="fa fa-caret-left"></span>{hyp.text}
				</div>
    );
  }
};


function Separator(props) {
  const {r,g,b} = props.modelData.color;
  const style = {cursor: "default",
           	 padding: "10px 15px 0px 15px",
		 backgroundColor:`rgba(${r},${g},${b}, 0.5)`};
  return (
    <RB.ListGroupItem>
      <RB.Table style={{marginBottom: "0"}}>
				<tbody>
					<tr>
						<td>
							<RB.Button disabled style={style}>
								<span><p>{Utils.getInitials(props.modelData.modelName)}</p></span>
							</RB.Button>
						</td>
						<td style={{padding:"20px 0 0 0"}}>
							<p style={{color:"grey",fontSize:"14px"}}>
								{Utils.shortenSeed(props.seed, 70)}
							</p>
						</td>
					</tr>
				</tbody>
      </RB.Table>
    </RB.ListGroupItem>
  );
}

function makeHypItems(hyps, models, onHypSelect, onHypDismiss) {
  let hypItems = [], lastSeed = null;
  for (var i=0; i<hyps.length; i++) {
    const hyp = hyps[i];
    const modelData = Utils.getModelData(models, hyp.model);
    const {r,g,b} = modelData.color;
    if (hyp.seed != lastSeed) {
      // hypItems.push(<Separator key={i} seed={hyp.seed} modelData={modelData}/>);
      lastSeed = hyp.seed;
    }
    hypItems.push(
      <HypItem
				key={hyp.id}
				hyp={hyp}
				backgroundColor={`rgba(${r},${g},${b}, 1)`}
				onHypSelect={onHypSelect}
				onHypDismiss={onHypDismiss}/>
		);
  }
  return hypItems;
}


class RegenerateButton extends React.Component {
  render() {
    let button;
    if (this.props.loadingHyps) {
      // show spinner
      button = (
				<RB.Button disabled style={{cursor: "default", padding:"4px 10px"}}>
					<Utils.Spinner/>
				</RB.Button>
			);
		} else {
			// show refresh button
			button = (
				<RB.Button
					onClick={this.props.onRegenerate}
					bsSize="sm"
					className="pull-right" >
					<i className="fa fa-refresh" id="refresh-button"/>
				</RB.Button>
			);
		}
    return button;
  }
}


class SuggestionList extends React.Component {

  scrollUp() {ReactDOM.findDOMNode(this).scrollTop = 0;}

  render () {
    const {hyps, models, onHypSelect, onHypDismiss} = this.props;
    return (
      <RB.ListGroup>
				<CSSTransitionGroup
					transitionName="dismiss"
					transitionEnterTimeout={500}
					transitionLeaveTimeout={150}>
					{makeHypItems(hyps, models, onHypSelect, onHypDismiss)}
				</CSSTransitionGroup>
      </RB.ListGroup>
    );
  }
}


class Suggestions extends React.Component {

  render() {
    const hasHyps = (this.props.hyps.length > 0) || this.props.loadingHyps || this.props.hasHadHyps;
    const collapsedClass = this.props.isCollapsed ? 'hidden' : '';
    const caretClass = this.props.isCollapsed ? 'fa fa-caret-up' : 'fa fa-caret-down';
    return (
      <div className={`suggestions-panel`}>
				<RB.Row>
					<SuggestionList
						ref="suggestionlist"
						hyps={this.props.hyps}
						models={this.props.models}
						onHypSelect={this.props.onHypSelect}
						onHypDismiss={this.props.onHypDismiss}/>
				</RB.Row>
				<RB.Row className={`${collapsedClass}`}>
					<RB.Button
						className="verwijder"
						bsSize="sm"
						style={{margin:"0 20px"}}
						onClick={() => {this.props.resetHyps(); this.props.onCollapse();}}>
						verwijder alle oude suggesties
					</RB.Button>
				</RB.Row>
      </div>
    );
  }
}

export default Suggestions;
