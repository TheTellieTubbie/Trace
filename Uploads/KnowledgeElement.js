import React from 'react';

export default class KnowledgeElement extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
        content : props.content ? props.content : undefined
      , stage : props.stage ? props.stage : 0
    };
  }
  
  render() {
    return (
      <div>{this.state.content}</div>
    );
  }
}

