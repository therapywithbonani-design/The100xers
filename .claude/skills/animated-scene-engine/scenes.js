// Scene library — add new scenes here. x = world position (px), props loop horizontally.
module.exports={
 filmset:{label:'Filmmaker on set',speed:110,burst:'ACTION!',caption:'TAKE 1...',kanji:'映画',tag:'Scene 1 · Take 3',
  props:[{type:'spot',x:40},{type:'chair',x:560},{type:'camera',x:820},{type:'tree',x:950},{type:'spot',x:1150},{type:'bush',x:600,layer:'near'}],
  chars:[{type:'person',x:330,carry:'clapper',beret:true,glasses:true,beard:true,scarf:true,colors:{shirt:'#f4f1ea',pants:'#2a2f45',hair:'#4a3020',skin:'#e8a882'}}]},
 dogwalk:{label:'Dog walk in the park',speed:130,burst:'WOOF!',kanji:'犬散歩',tag:'WALK 2.4 km',
  props:[{type:'tree',x:80},{type:'lamp',x:330},{type:'bench',x:560},{type:'tree',x:800},{type:'sign',x:1000,label:'PARK 88'},{type:'lamp',x:1080},{type:'bush',x:250,layer:'near'},{type:'bush',x:900,layer:'near'}],
  chars:[{type:'person',x:250,leash:true,carry:'leash'},{type:'dog',x:480}]},
 shopping:{label:'Shopping street haul',speed:120,burst:'SALE!',caption:'NEW DROP...',kanji:'買物',tag:'3 bags · ₹2,499',
  props:[{type:'store',x:150,label:'BOUTIQUE'},{type:'lamp',x:420},{type:'store',x:700,label:'SALE 50%'},{type:'tree',x:980},{type:'bush',x:500,layer:'near'}],
  chars:[{type:'person',x:340,carry:'bags'}]},
 cafe:{label:'Café coffee run',speed:100,burst:'SIP!',caption:'9:00 AM...',kanji:'珈琲',tag:'Latte · ₹180',
  props:[{type:'cafe',x:200,label:'CAFÉ'},{type:'tree',x:560},{type:'lamp',x:760},{type:'cafe',x:1000,label:'BAKERY'},{type:'bush',x:650,layer:'near'}],
  chars:[{type:'person',x:340,carry:'cup'}]},
};
