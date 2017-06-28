
import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider from 'rc-slider';

// Unused function for the addition of dropdown boxes.
function makeMenuItems(iterable, isActiveFn, getChildFn, onSelect) {
  let menuItems = [];
  for (var i=0; i<iterable.length; i++) {
    const item = iterable[i];
    menuItems.push(
      <RB.MenuItem
	 style={{"backgroundColor": isActiveFn(item) ? "darkseagreen" : "white"}}
	 eventKey={i}
	 key={i}
	 onSelect={(key, obj) => onSelect(iterable[key])}>
       {getChildFn(item)}
      </RB.MenuItem>
    );
  }
  return menuItems;
}

// make a set of buttons from an iterable. 
function makeButtons(iterable, isActiveFn, getChildFn, onSelect) {
  let buttons = [];
	var palette = ["#E39980", "#E3DA80", "#789DA7", "#A2CD74"]
	// TODO move the palette to a global variable of colours.
  for (var i=0; i<iterable.length; i++) {
    const model = iterable[i];
		var color = palette[i]
		if (model_names[model.path]) {
					var names = model_names[model.path].split(" ");
					var button_title = ""
					for (var n=0; n<names.length; n++) {
            button_title += names[n][0]
					}
    } else {
					var button_title = "XX"
    }

    buttons.push(
      <RB.Button bsStyle="primary" key={i} style={{backgroundColor:color, border:"1px solid black", color:"black"}}>
				{button_title}
      </RB.Button>
    );
  }
  return buttons;
}

class ButtonToolbar extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      models: []
    };
    this.updateModels = this.updateModels.bind(this);
    this.loadModel = this.loadModel.bind(this);			
  }

  componentDidMount() {
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: 'models',
      type: 'GET',
      dataType: 'json',
      success: (response) => this.setState({models: response.models}),
      error: (error) =>  console.log(error)
    });
  }

  updateModels(path, loaded) {
    if (!loaded) {
      return this.state.models;
    } else {
      return this.state.models.map(
	(model) => (model.path === path) ? {path: model.path, loaded: loaded} : model);
    }
  };

  loadModel(model) {
    if (model.loaded) {
      this.props.onModelSelect(model.path);
    } else {
      $.ajax({
	contentType: 'application/json;charset=UTF-8',
	url: 'load_model',
	type: 'POST',
	data: JSON.stringify({'model_name': model.path}),
	dataType: 'json',
	success: (response) => {
	  this.props.onModelSelect(response.model.path);
	  this.setState(
	    {models: this.updateModels(response.model.path, response.model.loaded)});
	},
	error: (error) =>  console.log(error)
      });
    }
  }
  
  render() {
    const {models} = this.state;
    const {temperature, currentModel, sizes, maxSeqLen, batchSizes, batchSize} = this.props;

		// Show Temperature
    const tempStr = (temperature.toString().length === 3) ?
	    temperature.toString() + '0' :
	    temperature;
    // create dropdown items for models
		let modelButtons;
    if (models.length > 0) {
      modelButtons = makeButtons(
                      models,
                      (model) => model.loaded,
                      (model) => model.path,
                      this.loadModel);
    } else {
      modelButtons = <RB.Button>No available models</RB.Button>;
    }
    return (
			<div className="generate-bar">
				<RB.ButtonToolbar horizontal>
					<RB.ButtonGroup style={{width: "200px", display: "inline-flex", margin: "7px 20px"}}>
						<span>Creativity</span>
						<Slider
								defaultValue={temperature} min={0.1} max={1.0} step={0.05}
								style={{width: "100%",margin: "3px 10px"}}
								onChange={this.props.onSliderChange}
								title="Creativity"
								/>
						<RB.Label style={{padding:"4px 8px"}}>{tempStr}</RB.Label>
					</RB.ButtonGroup>
					<RB.ButtonGroup style={{width: "200px", display: "inline-flex", margin: "7px 20px"}}>
						<span>Length</span>
						<Slider
								defaultValue={maxSeqLen} min={10} max={200} step={5}
								style={{width: "100%",margin: "3px 10px"}}
								onChange={this.props.onSeqLenChange}
								title="Length"
								/>
						<RB.Label style={{padding:"4px 8px"}}>{maxSeqLen}</RB.Label>
					</RB.ButtonGroup>
			<RB.ButtonGroup style={{float: "right"}} > 
				{modelButtons}
			</RB.ButtonGroup>
		</RB.ButtonToolbar>
		</div>
    );
  }
};

export default ButtonToolbar;
