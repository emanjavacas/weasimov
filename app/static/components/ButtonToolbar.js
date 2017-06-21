import React from 'react';
import ReactDom from 'react-dom';
import * as RB  from 'react-bootstrap';
import Slider from 'rc-slider';


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
    // create dropdown items for models
    let dropdownModels;
    if (models.length > 0) {
      dropdownModels = makeMenuItems(
	models,
	(model) => model.loaded,
	(model) => model.path,
	this.loadModel);
    } else {
      dropdownModels = <RB.MenuItem>No available models</RB.MenuItem>;
    }
    // create dropdown items for size
    const dropdownSizes = makeMenuItems(
      sizes,
      (size) => size === maxSeqLen,
      (size) => size,
      this.props.onSeqLenChange);
    // create dropdown items for batchSize
    const dropdownBatchSizes = makeMenuItems(
      batchSizes,
      (selectedBatchSize) => selectedBatchSize === batchSize,
      (batchSize) => batchSize,
      this.props.onBatchSizeChange);
    const tempStr = (temperature.toString().length === 3) ?
	    temperature.toString() + '0' :
	    temperature;
    return (
      <RB.Form horizontal>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Creativity
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
	    <RB.Row>
	      <RB.Col md={10}>
		<Slider
      		   defaultValue={temperature} min={0.1} max={1.0} step={0.05}
      		   style={{width: "100%", marginTop: "10px"}}
      		   onChange={this.props.onSliderChange}/>
	      </RB.Col>
	      <RB.Col md={2}>
		<RB.Label bsStyle="default" style={{verticalAlign:"bottom"}}>{tempStr}</RB.Label>
	      </RB.Col>
	    </RB.Row>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Model
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
      	    <RB.DropdownButton
      	       title={currentModel || "Model selection"}
      	       id="dropdown-model">
      	      {dropdownModels}
      	    </RB.DropdownButton>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Size
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
      	    <RB.DropdownButton
      	       title={maxSeqLen + " characters"}
      	       id="dropdown-size">
      	      {dropdownSizes}
      	    </RB.DropdownButton>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col componentClass={RB.ControlLabel} md={3} sm={4}>
	    Batch size
	  </RB.Col>
	  <RB.Col md={9} sm={8}>
      	    <RB.DropdownButton
      	       title={batchSize + " suggestions"}
      	       id="dropdown-size">
      	      {dropdownBatchSizes}
      	    </RB.DropdownButton>
	  </RB.Col>
	</RB.FormGroup>
	<RB.FormGroup>
	  <RB.Col smOffset={3} sm={9}>
	    <RB.Button
      	       bsStyle="primary"
      	       onClick={this.props.onGenerate}>
      	      Generate
      	    </RB.Button>
	  </RB.Col>
	</RB.FormGroup>
      </RB.Form>
    );
  }
};

export default ButtonToolbar;
