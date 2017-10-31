import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider from 'rc-slider';
import Utils from './Utils';


function makeButtons(models, onClick, selectmodel) {
	let buttons = [];
  for (var i=0; i<models.length; i++) {
    const model = models[i];
    const title = Utils.getInitials(model.modelName);
		const overlay = model.modelName ? model.modelName : model.path;
		let active = model.active;

    const borderWidth = model.loaded ? "1.5px" : "0.5px";
    const {r, g, b} = model.color;
		const backgroundColor = `rgb(${r},${g},${b})`;

    buttons.push(
      <RB.OverlayTrigger
				key={i}
				overlay={<RB.Tooltip id="tooltip">{overlay}</RB.Tooltip>}
				placement="bottom">
				<RB.Button
					bsStyle="primary"
					style={{backgroundColor: backgroundColor,
									borderColor: backgroundColor,
									color: "black"}}
					className={[active ? "selected" : "notselected","buttonname"].join(" ")}
					onClick={() => selectmodel(model,models)}>
					<span aria-hidden="true" className={active ? "fa fa-check-circle" : "fa fa-circle-o"}></span>{overlay}
        </RB.Button>
      </RB.OverlayTrigger>
    );
  }
  return buttons;
}


const noModelsButton = () => <RB.Button>No available models</RB.Button>;


class ButtonToolbar extends React.Component {
	constructor(props) {
		super(props);
		this.selectmodel = this.selectmodel.bind(this);
		this.props.models[Math.floor(Math.random() * (this.props.models.length - 1))].active = true;
	}
	selectmodel(model,models){
		for(var i in models){
			if(models[i].path === model.path) models[i].active = true;
			else models[i].active = false;
		}
		this.forceUpdate();
	}
  render() {
		const {temperature, maxSeqLen, models} = this.props;
    return (
      <div className="generate-bar">
				<div>
						{(models.length > 0) ? makeButtons(models, this.props.onGenerate, this.selectmodel) : noModelsButton}
				</div>
				<div className="sliders">
					<RB.ButtonGroup>
						<span>Creativiteit</span>
						<RB.Label>{temperature}</RB.Label>
						<Slider
							defaultValue={temperature} min={0.05} max={1.0} step={0.05}
							onChange={this.props.onTemperatureChange}
							title="Creativiteit"/>
						
					</RB.ButtonGroup>
					<RB.ButtonGroup>
						<span>Karakters</span>
						<RB.Label>{maxSeqLen}</RB.Label>
						<Slider
							defaultValue={maxSeqLen} min={10} max={200} step={5}
							onChange={this.props.onSeqLenChange}
							title="Lengte"/>
					</RB.ButtonGroup>
				</div>
				<div>
					<RB.Button
						className={["genereer",this.props.loadingHyps ? 'disabled' : ''].join(" ")}
						onClick={() => this.props.onGenerate(models)}>
							{this.props.loadingHyps ? 'AsiBot suggesties aan het laden...' : 'genereer suggesties'}
					</RB.Button>
					<label>{this.props.elapsed}</label>
				</div>
      </div>
    );
  }
};

export default ButtonToolbar;


