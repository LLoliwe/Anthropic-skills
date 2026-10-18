export const clamp=(v,min,max)=>Math.max(min,Math.min(max,v));
export function aimFromPoint(x,y){const dx=Math.max(1,x-60),dy=Math.max(1,310-y);return {speed:Math.round(clamp(Math.hypot(dx,dy)/5,5,40)),angle:Math.round(clamp(Math.atan2(dy,dx)*180/Math.PI,10,80))};}
export function synthFromPoint(x,y){return {frequency:Math.round(clamp(110+(x-40)/560*770,110,880)/10)*10,amplitude:Math.round(clamp(Math.abs(y-190)/125,0,1)*20)/20};}
export function scenePoint(rect,x,y){if(!rect.width||!rect.height)return null;const scale=Math.min(rect.width/640,rect.height/390);return {x:(x-rect.left-(rect.width-640*scale)/2)/scale,y:(y-rect.top-(rect.height-390*scale)/2)/scale};}
export function moleculeShape(formula){const shapes={
'H₂O':{atoms:[['O',320,160],['H',245,213],['H',395,213]],bonds:[[0,1,1],[0,2,1]]},
'CO₂':{atoms:[['C',320,170],['O',220,170],['O',420,170]],bonds:[[0,1,2],[0,2,2]]},
'NH₃':{atoms:[['N',320,140],['H',240,210],['H',320,225],['H',400,210]],bonds:[[0,1,1],[0,2,1],[0,3,1]]},
'CH₄':{atoms:[['C',320,175],['H',320,75],['H',225,190],['H',320,270],['H',415,190]],bonds:[[0,1,1],[0,2,1],[0,3,1],[0,4,1]]},
'O₂':{atoms:[['O',265,175],['O',375,175]],bonds:[[0,1,2]]},
'HCl':{atoms:[['H',270,175],['Cl',375,175]],bonds:[[0,1,1]]},
'SO₂':{atoms:[['S',320,145],['O',230,210],['O',410,210]],bonds:[[0,1,2],[0,2,2]]}
};return shapes[formula]||null;}
