export const KEY='lvl7-science-notebook-v1';
export function readProgress(){try{const s=JSON.parse(localStorage.getItem(KEY)||'{}');return {completed:s.completed&&typeof s.completed==='object'?s.completed:{},notes:Array.isArray(s.notes)?s.notes.filter(n=>typeof n.text==='string').slice(-100):[]};}catch{return {completed:{},notes:[]};}}
export function saveProgress(p){try{localStorage.setItem(KEY,JSON.stringify(p));return true;}catch{return false;}}
export function award(lab,mission,evidence){const p=readProgress(),key=lab+':'+mission,exists=!!p.completed[key];p.completed[key]={lab,mission,evidence};return {exists,saved:saveProgress(p)};}
