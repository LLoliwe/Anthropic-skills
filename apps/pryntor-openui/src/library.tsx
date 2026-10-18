import React from 'react';
import {createLibrary, defineComponent, createParser} from '@openuidev/react-lang';
import {z} from 'zod/v4';

export const lanes=['All','Pryntor','LVL7','BTWW','Tirisano'] as const;
export const states=['All','Ready','Review','Blocked'] as const;
export const tasks=[
 {id:'DEMO-01',lane:'Pryntor',title:'Release evidence, in one place.',detail:'Review the proof before advancing the release.',state:'Review'},
 {id:'DEMO-02',lane:'LVL7',title:'Make the first error visible.',detail:'A synthetic algebra review awaits an educator.',state:'Review'},
 {id:'DEMO-03',lane:'BTWW',title:'Build the dawn edition.',detail:'Original art direction is ready for an internal pass.',state:'Ready'},
 {id:'DEMO-04',lane:'Tirisano',title:'Keep the handoff human.',detail:'A fictional traveller enquiry needs route validation.',state:'Blocked'},
 {id:'DEMO-05',lane:'Pryntor',title:'Connect an approved runtime.',detail:'No worker is commissioned by this prototype.',state:'Blocked'},
];
export function selectTasks(lane:string,state:string){return tasks.filter(t=>(lane==='All'||t.lane===lane)&&(state==='All'||t.state===state));}
const Mission=defineComponent({name:'Mission',description:'Read-only synthetic venture work board. No tools or network actions.',props:z.object({lane:z.enum(lanes),state:z.enum(states)}),component:({props})=>{
 const rows=selectTasks(props.lane,props.state);
 return <section aria-label="Synthetic work board"><div className="board-heading"><h2>Next moves</h2><span role="status">{rows.length} demo items</span></div><div className="cards">{rows.map(t=><article key={t.id}><div className="card-top"><span>{t.lane}</span><span className={'badge '+t.state.toLowerCase()}>{t.state}</span></div><h3>{t.title}</h3><p>{t.detail}</p><footer>{t.id} · Synthetic example</footer></article>)}</div>{!rows.length&&<div className="empty"><h3>A clear lane.</h3><p>No demo work matches these filters.</p></div>}</section>;
}});
export const library=createLibrary({components:[Mission],root:'Mission'});
export function payload(lane:string,state:string){if(!lanes.includes(lane as any)||!states.includes(state as any))throw Error('Unsupported filter');return `root = Mission(${JSON.stringify(lane)}, ${JSON.stringify(state)})`;}
export function validatePayload(input:string){if(input.length>4096)throw Error('Payload exceeds limit');const parsed=createParser(library.toJSONSchema(),library.root).parse(input);if(parsed.meta.errors.length||parsed.meta.unresolved.length)throw Error('Invalid OpenUI payload');return parsed;}
