import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import firebase from "firebase";


const firebaseConfig = {
  apiKey: "AIzaSyCoOe8iKgg6Oq5v63V3vG3m6SbBF2kX3aA",
  authDomain: "benscrappydndthing.firebaseapp.com",
  projectId: "benscrappydndthing",
  storageBucket: "benscrappydndthing.appspot.com",
  messagingSenderId: "867405045505",
  appId: "1:867405045505:web:c7183a8fe2f07f85b3c500",
  measurementId: "G-S5YMMWHDGY"
};

firebase.initializeApp(firebaseConfig);
//const auth = firebase.auth;
const db = firebase.database().ref();

class Square extends React.Component {
  constructor(props) {
    super(props);
  }
  draw_players()
  {
    const colors = ["#008800","#880000","#000088","#008888","#888800","#880088"];
    const light_colors = ["#00FF00","#FF0000","#0000FF","#00FFFF","#FFFF00","#FF00FF"];
    if(this.props.value.player){
      let id = this.props.value.player.id;
      while(id >= 6)
      {
        id -= 6;
      }
      return(<style className="circle" style={{background: colors[id]}}/>)
    }
    else if(this.props.value.potplay)
    {
    let id = this.props.value.potplay.id;
      while(id >= 6)
      {
        id -= 6;
      }
      return(<style className="circle" style={{background: light_colors[id]}}/>)
    }
    else
    {
      return(null)
    }
  }
  draw_path()
  {
    const out_style = [{class:"downslope",top:0,left:0},
    {class:"vertline",top:0,left:0},
    {class:"upslope",top:0,left:16},
    {class:"hozline",top:0,left:0},
    {class:"hozline",top:0,left:16},
    {class:"hozline",top:0,left:16},
    {class:"upslope",top:16,left:0},
    {class:"vertline",top:16,left:0},
    {class:"downslope",top:16,left:16}
    ]
    const light_colors = ["#00FF00","#FF0000","#0000FF","#00FFFF","#FFFF00","#FF00FF"];
    var offset = 0
    if (this.props.value.potplay||this.props.value.player)
    {
      offset = -33;
    }
    var return_thing = []
    for(let i = 0;i<this.props.value.outs.length;i++)
    {
      let id = this.props.value.outs[i].id;
      while(id >= 6)
      {
        id -= 6;
      }
      return_thing.push(<div class={out_style[this.props.value.outs[i].move].class} style={{top:out_style[this.props.value.outs[i].move].top,left:out_style[this.props.value.outs[i].move].left,borderBottomColor:light_colors[id]}}/>)
        //this.props.value.outs[i].move
    }
        for(let i = 0;i<this.props.value.ins.length;i++)
    {
      let id = this.props.value.ins[i].id;
      while(id >= 6)
      {
        id -= 6;
      }
      return_thing.push(<div class={out_style[8-this.props.value.ins[i].move].class} style={{top:out_style[8-this.props.value.ins[i].move].top,left:out_style[8-this.props.value.ins[i].move].left,borderBottomColor:light_colors[id]}}/>)
        //this.props.value.outs[i].move
    }
    

    return(<div class="background" style={{top:offset}}>
      {return_thing}
      </div>)
  }

  render()
  {    
    var bg = "white"
    if(this.props.value.selected)
    {
      bg = "aqua"
    }
    return (
      <button className="square" onClick={this.props.onClick} style={{background: bg}}>
        {this.draw_players()}
        {this.draw_path()}
      </button>
    )
  }
}

function DirButt(props) {
  return (
    <button className="direction" onClick={props.onClick}>
    {props.value}
    </button>
    )
}

function ControlButt(props) {
  return  (
    <button onClick={props.onClick}>
    {props.value}
    </button>
    )
}

class Board extends React.Component {
  renderSquare(i) {
    return (
      <Square
        value={this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
      />
    );
  }
  createMap(){

    let rows = []
    
    for(let i =0; i<14;i++)
    {
      let column = [];
      for(let ii =0; ii<14;ii++)
      {
        column.push(this.renderSquare((i*14)+ii))
      }
      rows.push(<div className="board-row">{column}</div>);
    }

    return(<div>{rows}</div>);
  }

  render() {
    return (
      this.createMap()
    );
  }
}

class Directional extends React.Component {
  renderSquare(i) {
    const Symbols = ['\u{1f884}','\u{1f881}','\u{1f885}','\u{1f880}','\u{2b24}','\u{1f882}','\u{1f887}','\u{1f883}','\u{1f886}']
    return (
      <DirButt
        value={Symbols[i]}
        onClick={() => this.props.onClick(i)}
      />
    );
  }

  render() {
    return (
      <div>
        <div className="board-row">
          {this.renderSquare(0)}
          {this.renderSquare(1)}
          {this.renderSquare(2)}

        </div>
        <div className="board-row">
          {this.renderSquare(3)}
          {this.renderSquare(4)}
          {this.renderSquare(5)}

        </div>
        <div className="board-row">
          {this.renderSquare(6)}
          {this.renderSquare(7)}
          {this.renderSquare(8)}

        </div>
      </div>
    );
  }
}



class Game extends React.Component {
  constructor(props) {
    super(props);
    this.state ={square_info:Array(255).fill(0),players:[],current_selected:{player:0,index:0,movepot:0},square_selected:0,orderque:[]}
    for (let i = 0;i<this.state.square_info.length;i++)
    {
      this.state.square_info[i] = {player:null,selected:false,potplay:null,ins:[],outs:[]}
    }
//    this.state.players.push({name:"player1",id:1,location:55})
//    this.state.players.push({name:"player2",id:2,location:0})
//    this.state.square_info[55].player = this.state.players[0]
//    this.state.square_info[0].player = this.state.players[1]
//    this.state.square_info[0].selected = true;
    this.init_database()
    this.start_database()

    console.log(this.state)
  }

  init_database()
  {
    //var newplayers = []
    db.child("Players").get().then((snapshot) => {
      if (snapshot.exists()) {
        console.log(snapshot.val());
        this.load_database(snapshot.val())
      } else {
        console.log("No data available");
      }
    }).catch((error) => {
  console.error(error);
  });
  }
  start_database()
  {
    db.child("Players").on('value',(snapshot) => {
      if (snapshot.exists()) {
        console.log(snapshot.val());
        this.load_database(snapshot.val())
        console.log("database update")
      } else {
        console.log("No data available");
      }
    });
  }

  load_database(newplayers)
  {
    for (let i = 0;i<this.state.square_info.length;i++)
      {
        this.state.square_info[i].player = null;
      }
      this.state.players = [];//For future reference probs dont need to clear the whole thing when ever anyone updates
      for(let i = 0;i<newplayers.length;i++)
        {
          this.state.players.push(newplayers[i])
          this.state.square_info[this.state.players[this.state.players.length-1].location].player = this.state.players[this.state.players.length-1]
          
        }
        console.log(this.state)
        this.setState(this.state);
  }

  handleClick(i) {
    console.log("Square" + i +"click");
    this.clear_move()
    if(this.state.square_info[i].player)
    {
    	console.log("There is a player there")
    	this.state.current_selected.player = this.state.square_info[i].player;
      this.state.current_selected.movepot = this.state.square_info[i].player.location;
      for(var j = 0;j<this.state.players.length;j++)
      {
        if(this.state.players[j].id === this.state.current_selected.player.id)
        {
          this.state.current_selected.index = j;
        }
      }
      //this.state.current_selected.index = j;  
      console.log(this.state.current_selected)



    }
    this.state.square_info[this.state.square_selected].selected = false;
    this.state.square_info[i].selected = true;
    this.state.square_selected = i;
    this.setState(this.state);
    
  }

  handleButton(i)
  {
  	console.log("Button " + i +" clicked");
  	
  	let current_square = this.state.current_selected.movepot;//this.state.players[this.state.current_selected.index].location
  	let next_square = current_square;
    let move_pass = false;

  	switch(i){
  		case 0:
      if(current_square%14>0)
      {
        if(current_square > 14)
        {
        next_square -= 15;
        move_pass = true;
        }
      }
  		break;
  		case 1:
      if(current_square > 14)
      {
  		  next_square -= 14;
        move_pass = true;
      }
  		break;
  		case 2:
      if(current_square%14<13)
      {
        if(current_square > 14)
        {
  		  next_square -= 13;
        move_pass = true;
        }
      }
  		break;
  		case 3:
      if(current_square%14>0)
      {
  		  next_square -= 1;
        move_pass = true;
      }
  		break;
  		case 4:
  		next_square += 0;
      this.state.square_info[this.state.players[this.state.current_selected.index].location].player = null
      this.state.square_info[current_square].player = this.state.players[this.state.current_selected.index];
      this.state.players[this.state.current_selected.index].location = current_square;
      db.child("Players").update(this.state.players)
      this.state.orderque.push("MagOFF")
      db.child("Que").push(this.state.orderque)
      this.clear_move()
  		break;
  		case 5:
      {
      if(current_square%14<13)
  		  next_square += 1;
        move_pass = true;
  		break;
      }
  		case 6:
      if(current_square%14>0)
  		  next_square += 13;
        move_pass = true;
  		break;
  		case 7:
  		  next_square += 14;
        move_pass = true;
  		break;
  		case 8:
      if(current_square%14<13)
      {
  		  next_square += 15;
        move_pass = true;
      }
  		break;
  	}

    const orders = ["NW","N","NE","W","W","E","SW","S","SE"]

  	if(next_square >= 0 && next_square < 196 && !this.state.square_info[next_square].player)
  	{
      if(move_pass)
      {
        this.state.square_info[current_square].outs.push({move:i,id:this.state.players[this.state.current_selected.index].id})
        this.state.square_info[next_square].ins.push({move:i,id:this.state.players[this.state.current_selected.index].id})
  		  console.log("Move to" + next_square);
        if(current_square == this.state.players[this.state.current_selected.index].location)
        {
          this.state.orderque.push("GOTO:"+current_square.toString())
          this.state.orderque.push("MagON")
        }
        this.state.orderque.push(orders[i])
        this.state.current_selected.movepot = next_square;
        this.state.square_info[current_square].potplay = null;
        this.state.square_info[next_square].potplay = this.state.players[this.state.current_selected.index];
      //this.state.players[this.state.current_selected.index].location = next_square;
  		//this.state.square_info[current_square].player = null;
      //this.state.square_info[next_square].player = this.state.players[this.state.current_selected.index];
  	}
  	this.setState(this.state);
    }


  }
  new_char() {
    //let gameinfo = this.state;
    if(!this.state.square_info[this.state.square_selected].player)
      {
      let id = 1;
      if(this.state.players.length)
      {
        id = this.state.players[this.state.players.length-1].id+1;
      }
      this.state.players.push({name:"player"+id.toString(),id:id,location:this.state.square_selected})
      this.state.square_info[this.state.square_selected].player = this.state.players[this.state.players.length-1];
      this.handleClick(this.state.square_selected)
      if(this.state.players.length<1)
      {
        db.push({Players:this.state.players})
      }
      else
      {
        db.child("Players").update(this.state.players)
      }
    }
    else
    {
      alert("YO there is already a player there")
    }
    //this.setState(this.state);

    console.log("new_char")
  }
  delete_char() {
    console.log("delete_char")
    for(let i = this.state.current_selected.index;i < this.state.players.length-1;i++)
    {
      this.state.players[i] = this.state.players[i+1];
    }
    
    this.state.players.pop()
    db.child("Players").update(this.state.players)
    db.child("Players").child((this.state.players.length-1).toString()).remove()
    this.init_database()
    this.setState(this.state)

  }
  clear_move() {
    console.log("clear_move")
    for (let i = 0;i<this.state.square_info.length;i++)
    {
      this.state.square_info[i].selected = false;
      this.state.square_info[i].potplay = null
      this.state.square_info[i].ins = []
      this.state.square_info[i].outs   = []
    }
    if(this.state.square_info[this.state.current_selected.index].player)
    {
    this.state.current_selected.movepot = this.state.square_info[this.state.current_selected.index].player.location;
    }
    this.state.orderque = [];
    this.setState(this.state)
  }
  get_info()  {
    db.child("Players").child("play1").child("Position").get().then((snapshot) => {
      if (snapshot.exists()) {
        console.log(snapshot.val());
      } else {
        console.log("No data available");
      }
    }).catch((error) => {
  console.error(error);
  });
  }


  render() {
  	//const gameinfo = this.state
    return (
      <div className="game">
        <div className="game-board">
          <Board
            squares={this.state.square_info}
            onClick={i => this.handleClick(i)}
          />
          <button onClick={() => this.new_char()}>
            new char
          </button>
          <button onClick={() => {alert("This Button No Longer Works BECAUSE WE CANT HAVE NICE THINGS GET BENT BRANDON")}}>
            delete char
          </button>
          <button onClick={() => this.clear_move()}>
            clear move
          </button>
          <button onClick={() => this.get_info()}>
            char info
          </button>
        </div>
        <div className="game-board">
          <Directional
              onClick={i => this.handleButton(i)}
          />
        </div> 
      </div> 
    );
  }
}

// ========================================

ReactDOM.render(<Game />, document.getElementById("root"));
