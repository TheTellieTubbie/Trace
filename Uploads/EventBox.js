import React from 'react';
import { DropTarget } from 'react-dnd';
import MathJax from 'react-mathjax';

import psv from './PSV';
import ModelBox, { DropHandler } from './ModelBox';
import Variable from './Variable';
import Function from './Function';
import Tool from './Tool';

class EventBox extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        boxes : props.variables ? props.variables : []
      , direction : (props.direction === "receive") ? "receive" : "send"
      , preprocess : props.preprocess ? props.preprocess : undefined
    };
    
  }
  
  toPSV = () => {
    return (
      // TODO: send is not the right direction
      <event type="send">
        {this.state.boxes.map((e) => <variable id={e.props.name}></variable>)}
      </event>
    );
  }
  
  render() {
    const { isOver, canDrop, connectDropTarget } = this.props;
    
    var arrow = "img/";
    switch (this.state.direction) {
      case "receive":
        arrow += "arrow-receive.svg";
        break;
        
      case "send":
      default:
        arrow += "arrow-send.svg";
        break;
    }
    
    var formula = this.state.boxes.map((v) =>
          v.props.name
        ).join(',');
        
    const emptyClass = (this.state.boxes.length === 0) ? "modelbox-empty" : "";
    
    const dragClass = (isOver && canDrop)
      ? "drag-over"
      : (canDrop
        ? "drag-accepting"
        : ""
      );
      
    const className = emptyClass + " rounded " + (this.props.className ? this.props.className : "") + " " + dragClass;
    
    return connectDropTarget(
      <div className="eventbox">
        <MathJax.Provider>
          <MathJax.Node className={className} formula={formula} />
        </MathJax.Provider>
        <object type="image/svg+xml" data={arrow}>
          Your browser does not support svg images
        </object>
      </div>
    );
  }
}

/**
 * Drop handling 
 */
const acceptCriteria = [
    (o) => (o.type === <Tool />.type && o.props.object.type === <Variable />.type)
  , (o) => (o.type === <Tool />.type && o.props.object.type === <Function />.type && o.props.object.props.arity === 0)
];

export default DropTarget('Tool', DropHandler.generateEvents(acceptCriteria, ), DropHandler.eventCollector)(psv(EventBox))
